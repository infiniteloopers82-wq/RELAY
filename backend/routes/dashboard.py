from flask import Blueprint,jsonify
from routes.auth import login_required,current_user,roles
from models.resource import Resource
from models.booking import Booking
from models.incident import Incident
from models.audit_log import AuditLog
bp=Blueprint('dashboard',__name__,url_prefix='/api/dashboard')

@bp.get('/student')
@login_required
def student():
    u=current_user(); rows=Booking.query.filter_by(user_id=u.id).order_by(Booking.created_at.desc()).all()
    return jsonify({'summary':{'upcoming':sum(b.status=='approved' for b in rows),'active':sum(b.status=='checked_in' for b in rows),'requests':len(rows)},'bookings':[b.to_dict() for b in rows]})
@bp.get('/owner')
@login_required
def owner():
    u=current_user(); ids=[r.id for r in Resource.query.filter_by(owner_id=u.id).all()] if u.role!='admin' else [r.id for r in Resource.query.all()]
    rows=Booking.query.filter(Booking.resource_id.in_(ids)).order_by(Booking.created_at.desc()).all() if ids else []
    return jsonify({'summary':{'resources':len(ids),'pending':sum(b.status=='pending' for b in rows),'waitlisted':sum(b.status=='waitlisted' for b in rows)},'bookings':[b.to_dict() for b in rows]})
@bp.get('/admin')
@roles('admin')
def admin():
    return jsonify({'summary':{'resources':Resource.query.count(),'bookings':Booking.query.count(),'incidents':Incident.query.count(),'audit_events':AuditLog.query.count()}})

@bp.get('/audit-logs')
@roles('admin')
def audit_route():
    return jsonify({'audit_logs':[x.to_dict() for x in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()]})
