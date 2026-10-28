from extensions import db
from models.audit_log import AuditLog

def audit(actor, action, entity_type, entity_id, reason=None, metadata=None):
    log=AuditLog(actor_id=actor.id if actor else None,action=action,entity_type=entity_type,entity_id=entity_id,reason=reason,metadata_json=metadata)
    db.session.add(log)
