from datetime import datetime
from extensions import db
class ConditionReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    stage = db.Column(db.String(20), nullable=False)
    condition_description = db.Column(db.Text, nullable=False)
    image_reference = db.Column(db.String(300))
    reporting_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    booking = db.relationship('Booking', backref='condition_reports')
    reporting_user = db.relationship('User')
    def to_dict(self): return {'id':self.id,'booking_id':self.booking_id,'stage':self.stage,'condition_description':self.condition_description,'image_reference':self.image_reference,'reporting_user_id':self.reporting_user_id,'created_at':self.created_at.isoformat()}
