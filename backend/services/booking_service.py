from datetime import datetime, timezone
from extensions import db
from models.booking import Booking
from models.resource import Resource
from services.eligibility import eligible
from services.audit_service import audit

def overlap(resource_id,start,end,exclude_id=None):
    q=Booking.query.filter(Booking.resource_id==resource_id,Booking.status.in_(['approved','checked_in']),Booking.start_at<end,Booking.end_at>start)
    if exclude_id: q=q.filter(Booking.id != exclude_id)
    return q.first()

def create_booking(user,data):
    resource=db.session.get(Resource,int(data['resource_id']))
    if not resource or not resource.active: raise ValueError('Resource is unavailable')
    try: start=datetime.fromisoformat(data['start_at'].replace('Z','+00:00')); end=datetime.fromisoformat(data['end_at'].replace('Z','+00:00'))
    except (ValueError,KeyError,TypeError): raise ValueError('Valid ISO start_at and end_at values are required')
    if start.tzinfo: start=start.astimezone(timezone.utc).replace(tzinfo=None)
    if end.tzinfo: end=end.astimezone(timezone.utc).replace(tzinfo=None)
    if start >= end: raise ValueError('start_at must precede end_at')
    if overlap(resource.id,start,end):
        existing=True
    else: existing=False
    ok,reasons=eligible(user,resource)
    status='pending'
    allocation='Standard first-requested queue'
    if not ok:
        status='waitlisted'; allocation='Waitlisted: ' + '; '.join(reasons)
    elif existing:
        status='waitlisted'; allocation='Waitlisted: Requested time conflicts with another active request'
    b=Booking(resource_id=resource.id,user_id=user.id,start_at=start,end_at=end,purpose=data.get('purpose',''),status=status,allocation_reason=allocation)
    db.session.add(b); db.session.flush()
    audit(user,'booking_created','booking',b.id,allocation)
    if status=='waitlisted': refresh_waitlist(resource.id)
    return b

def refresh_waitlist(resource_id):
    rows=Booking.query.filter_by(resource_id=resource_id,status='waitlisted').order_by(Booking.created_at,Booking.id).all()
    for i,b in enumerate(rows,1): b.waitlist_position=i
