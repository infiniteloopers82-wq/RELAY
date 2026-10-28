from datetime import datetime
from flask import Blueprint,request,jsonify
from extensions import db
from models.booking import Booking,TRANSITIONS
from models.resource import Resource
from models.condition_report import ConditionReport
from routes.auth import login_required,current_user
from services.booking_service import create_booking,overlap,refresh_waitlist
from services.eligibility import eligible
from services.audit_service import audit
bp=Blueprint('bookings',__name__,url_prefix='/api/bookings')

def personnel(u,r): return u.role=='admin' or u.id==r.owner_id

@bp.get('')
@login_required
def list_bookings():
    u=current_user(); q=Booking.query
    if u.role=='student': q=q.filter_by(user_id=u.id)
    elif u.role=='owner':
        ids=[r.id for r in Resource.query.filter_by(owner_id=u.id).all()]; q=q.filter(Booking.resource_id.in_(ids)) if ids else q.filter(False)
    return jsonify({'bookings':[b.to_dict() for b in q.order_by(Booking.created_at.desc()).all()]})

@bp.get('/<int:id>')
@login_required
def detail(id):
    u=current_user(); b=db.session.get(Booking,id)
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if u.role=='student' and b.user_id!=u.id: return jsonify({'error':'Forbidden','code':'forbidden'}),403
    if u.role=='owner' and b.resource.owner_id!=u.id: return jsonify({'error':'Forbidden','code':'forbidden'}),403
    return jsonify({'booking':b.to_dict(),'condition_reports':[r.to_dict() for r in b.condition_reports]})

@bp.post('')
@login_required
def create():
    try:
        b=create_booking(current_user(),request.get_json(silent=True) or {})
        db.session.commit(); refresh_waitlist(b.resource_id); db.session.commit()
        return jsonify({'booking':b.to_dict()}),201
    except (ValueError,KeyError,TypeError) as e:
        db.session.rollback(); return jsonify({'error':str(e),'code':'validation_error'}),400

@bp.post('/<int:id>/approve')
@login_required
def approve(id):
    u=current_user(); b=db.session.get(Booking,id)
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if b.resource.owner_id==u.id and u.role!='admin': pass
    if not personnel(u,b.resource): return jsonify({'error':'Only the resource owner or administrator may approve','code':'forbidden'}),403
    if b.user_id==u.id and u.role!='admin': return jsonify({'error':'Owners cannot approve their own request','code':'forbidden'}),403
    ok,reasons=eligible(b.user,b.resource)
    if not ok: return jsonify({'error':'Requester is not eligible','code':'ineligible','reasons':reasons}),409
    active=Booking.query.filter_by(resource_id=b.resource_id,user_id=b.user_id,status='approved').count() + Booking.query.filter_by(resource_id=b.resource_id,user_id=b.user_id,status='checked_in').count()
    if active >= b.resource.usage_limit: return jsonify({'error':'User booking limit reached','code':'limit_reached'}),409
    if overlap(b.resource_id,b.start_at,b.end_at,b.id): return jsonify({'error':'Time conflicts with an approved or active booking','code':'conflict'}),409
    if b.status not in ('pending','waitlisted'): return jsonify({'error':f'Cannot approve booking in {b.status} state','code':'invalid_transition'}),409
    d=request.get_json(silent=True) or {}; reason=d.get('reason','Approved by owner')
    b.status='approved'; b.waitlist_position=None; b.decision_reason=reason
    refresh_waitlist(b.resource_id); audit(u,'booking_approved','booking',b.id,reason); db.session.commit(); return jsonify({'booking':b.to_dict()})

@bp.post('/<int:id>/reject')
@login_required
def reject(id):
    u=current_user(); b=db.session.get(Booking,id)
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if not personnel(u,b.resource): return jsonify({'error':'Forbidden','code':'forbidden'}),403
    d=request.get_json(silent=True) or {}
    if b.status not in ('pending','waitlisted'): return jsonify({'error':'Invalid booking transition','code':'invalid_transition'}),409
    if not d.get('reason'): return jsonify({'error':'Rejection reason is required','code':'validation_error'}),400
    b.status='rejected'; b.decision_reason=d['reason']; b.waitlist_position=None
    refresh_waitlist(b.resource_id); audit(u,'booking_rejected','booking',b.id,d['reason']); db.session.commit(); return jsonify({'booking':b.to_dict()})

@bp.post('/<int:id>/cancel')
@login_required
def cancel(id):
    u=current_user(); b=db.session.get(Booking,id)
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if u.role!='admin' and b.user_id!=u.id: return jsonify({'error':'Forbidden','code':'forbidden'}),403
    if 'cancelled' not in TRANSITIONS.get(b.status,set()) and b.status!='approved': return jsonify({'error':'Invalid booking transition','code':'invalid_transition'}),409
    b.status='cancelled'; b.waitlist_position=None; refresh_waitlist(b.resource_id)
    audit(u,'booking_cancelled','booking',b.id,(request.get_json(silent=True) or {}).get('reason')); db.session.commit(); return jsonify({'booking':b.to_dict()})

def condition_transition(b,status,stage,u,d):
    if b.status=='approved' and stage=='check-in': return True
    if b.status=='checked_in' and stage=='return': return True
    return False

@bp.post('/<int:id>/check-in')
@login_required
def check_in(id):
    u=current_user(); b=db.session.get(Booking,id); d=request.get_json(silent=True) or {}
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if u.role!='admin' and b.user_id!=u.id and b.resource.owner_id!=u.id: return jsonify({'error':'Forbidden','code':'forbidden'}),403
    if b.status!='approved': return jsonify({'error':'Booking must be approved before check-in','code':'invalid_transition'}),409
    if not d.get('condition_description'): return jsonify({'error':'Condition description is required','code':'validation_error'}),400
    b.status='checked_in'; b.check_in_at=datetime.utcnow(); db.session.flush(); db.session.add(ConditionReport(booking_id=b.id,stage='check-in',condition_description=d['condition_description'],image_reference=d.get('image_reference'),reporting_user_id=u.id))
    audit(u,'booking_checked_in','booking',b.id); db.session.commit(); return jsonify({'booking':b.to_dict()})

@bp.post('/<int:id>/return')
@login_required
def return_booking(id):
    u=current_user(); b=db.session.get(Booking,id); d=request.get_json(silent=True) or {}
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if u.role!='admin' and b.user_id!=u.id and b.resource.owner_id!=u.id: return jsonify({'error':'Forbidden','code':'forbidden'}),403
    if b.status!='checked_in': return jsonify({'error':'Booking must be checked in before return','code':'invalid_transition'}),409
    if not d.get('condition_description'): return jsonify({'error':'Condition description is required','code':'validation_error'}),400
    b.status='returned'; b.return_at=datetime.utcnow(); db.session.flush(); db.session.add(ConditionReport(booking_id=b.id,stage='return',condition_description=d['condition_description'],image_reference=d.get('image_reference'),reporting_user_id=u.id))
    audit(u,'booking_returned','booking',b.id); db.session.commit(); return jsonify({'booking':b.to_dict()})
