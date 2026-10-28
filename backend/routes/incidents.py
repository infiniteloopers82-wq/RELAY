from flask import Blueprint,request,jsonify
from extensions import db
from models.incident import Incident
from models.booking import Booking
from routes.auth import login_required,current_user
from services.audit_service import audit
bp=Blueprint('incidents',__name__,url_prefix='/api/incidents')

@bp.get('')
@login_required
def list_incidents():
    u=current_user()
    q=Incident.query
    if u.role=='student': q=q.filter_by(reporter_id=u.id)
    return jsonify({'incidents':[x.to_dict() for x in q.order_by(Incident.created_at.desc()).all()]})

@bp.post('')
@login_required
def report():
    u=current_user(); d=request.get_json(silent=True) or {}; b=db.session.get(Booking,int(d.get('booking_id',0)))
    if not b: return jsonify({'error':'Booking not found','code':'not_found'}),404
    if b.user_id!=u.id and u.role!='admin': return jsonify({'error':'You cannot report this booking','code':'forbidden'}),403
    if not d.get('description'): return jsonify({'error':'Description is required','code':'validation_error'}),400
    i=Incident(booking_id=b.id,reporter_id=u.id,description=d['description'],severity=d.get('severity','medium'))
    db.session.add(i); db.session.flush(); audit(u,'incident_reported','incident',i.id); db.session.commit()
    return jsonify({'incident':i.to_dict()}),201

@bp.post('/<int:id>/review')
@login_required
def review(id):
    u=current_user(); i=db.session.get(Incident,id)
    if u.role=='student': return jsonify({'error':'Personnel permission required','code':'forbidden'}),403
    if not i: return jsonify({'error':'Incident not found','code':'not_found'}),404
    i.review_status='reviewing'; i.reviewer_id=u.id; audit(u,'incident_reviewed','incident',i.id); db.session.commit(); return jsonify({'incident':i.to_dict()})

@bp.post('/<int:id>/resolve')
@login_required
def resolve(id):
    u=current_user(); i=db.session.get(Incident,id); d=request.get_json(silent=True) or {}
    if u.role=='student': return jsonify({'error':'Personnel permission required','code':'forbidden'}),403
    if not i: return jsonify({'error':'Incident not found','code':'not_found'}),404
    if not d.get('resolution_notes'): return jsonify({'error':'Resolution notes are required','code':'validation_error'}),400
    i.review_status='resolved'; i.resolution_notes=d['resolution_notes']; i.reviewer_id=u.id
    audit(u,'incident_resolved','incident',i.id,metadata=d['resolution_notes']); db.session.commit(); return jsonify({'incident':i.to_dict()})
