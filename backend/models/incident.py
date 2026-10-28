from datetime import datetime
from extensions import db
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default='medium')
    review_status = db.Column(db.String(20), nullable=False, default='reported')
    resolution_notes = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    booking = db.relationship('Booking', backref='incidents')
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    def to_dict(self): return {'id':self.id,'booking_id':self.booking_id,'reporter_id':self.reporter_id,'reporter_name':self.reporter.name,'description':self.description,'severity':self.severity,'review_status':self.review_status,'resolution_notes':self.resolution_notes,'reviewer_id':self.reviewer_id,'created_at':self.created_at.isoformat(),'updated_at':self.updated_at.isoformat() if self.updated_at else None}
