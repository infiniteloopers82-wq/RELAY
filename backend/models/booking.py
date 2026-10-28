from datetime import datetime
from extensions import db

STATUSES = {'pending','waitlisted','approved','checked_in','returned','cancelled','rejected'}
TRANSITIONS = {'pending':{'approved','rejected','cancelled','waitlisted'},'waitlisted':{'cancelled','approved','rejected'},'approved':{'cancelled','checked_in'},'checked_in':{'returned'},'returned':set(),'cancelled':set(),'rejected':set()}
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    decision_reason = db.Column(db.Text)
    allocation_reason = db.Column(db.Text)
    waitlist_position = db.Column(db.Integer)
    check_in_at = db.Column(db.DateTime)
    return_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resource = db.relationship('Resource', backref='bookings')
    user = db.relationship('User', backref='bookings')
    def to_dict(self):
        return {'id':self.id,'resource_id':self.resource_id,'resource_name':self.resource.name if self.resource else None,'user_id':self.user_id,'user_name':self.user.name if self.user else None,'start_at':self.start_at.isoformat(),'end_at':self.end_at.isoformat(),'purpose':self.purpose,'status':self.status,'decision_reason':self.decision_reason,'allocation_reason':self.allocation_reason,'waitlist_position':self.waitlist_position,'check_in_at':self.check_in_at.isoformat() if self.check_in_at else None,'return_at':self.return_at.isoformat() if self.return_at else None,'created_at':self.created_at.isoformat()}
