from flask import Blueprint,jsonify
from routes.auth import roles
from models.audit_log import AuditLog
bp=Blueprint('audit',__name__,url_prefix='/api/audit-logs')
@bp.get('')
@roles('admin')
def logs(): return jsonify({'audit_logs':[x.to_dict() for x in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()]})
