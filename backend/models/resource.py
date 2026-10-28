from datetime import datetime
from extensions import db

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default='')
    category = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(160), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    availability = db.Column(db.String(240), default='Mon–Fri, 9:00–18:00')
    access_requirements = db.Column(db.Text, default='')
    training_required = db.Column(db.String(80), default='')
    supervision_required = db.Column(db.Boolean, default=False)
    usage_limit = db.Column(db.Integer, default=3)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_resources')
    def to_dict(self):
        return {'id':self.id,'name':self.name,'description':self.description,'category':self.category,'location':self.location,'owner_id':self.owner_id,'owner_name':self.owner.name if self.owner else None,'availability':self.availability,'access_requirements':self.access_requirements,'training_required':self.training_required,'supervision_required':self.supervision_required,'usage_limit':self.usage_limit,'active':self.active,'created_at':self.created_at.isoformat()}
