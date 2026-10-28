from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    institution_status = db.Column(db.String(80), nullable=True)
    training_status = db.Column(db.String(80), nullable=False, default='untrained')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def to_dict(self):
        return {'id':self.id,'name':self.name,'email':self.email,'role':self.role,'institution_status':self.institution_status,'training_status':self.training_status,'created_at':self.created_at.isoformat()}
