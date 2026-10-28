from datetime import datetime
from extensions import db
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.Integer)
    reason = db.Column(db.Text)
    metadata_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actor = db.relationship('User')
    def to_dict(self): return {'id':self.id,'actor_id':self.actor_id,'actor_name':self.actor.name if self.actor else 'System','action':self.action,'entity_type':self.entity_type,'entity_id':self.entity_id,'reason':self.reason,'metadata':self.metadata_json,'created_at':self.created_at.isoformat()}
