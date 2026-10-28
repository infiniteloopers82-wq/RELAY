from datetime import datetime,timedelta
from extensions import db
from models import Resource,Booking,AuditLog
from conftest import create_user

def login(client,email): return client.post('/api/auth/login',json={'email':email,'password':'Password123!'})
def add_resource(owner,name='Demo Scope',training=''):
    r=Resource(name=name,description='Demo equipment',category='Electronics',location='Lab',owner_id=owner.id,training_required=training,active=True,usage_limit=3);db.session.add(r);db.session.commit();return r
def payload(resource,start=None,end=None):
    start=start or datetime.utcnow()+timedelta(days=1);end=end or start+timedelta(hours=2)
    return {'resource_id':resource.id,'start_at':start.isoformat(),'end_at':end.isoformat(),'purpose':'Project work'}

def test_health(client): assert client.get('/api/health').status_code==200

def test_register_login_password_hash(client,app):
    r=client.post('/api/auth/register',json={'name':'Test User','email':'USER@relay.test','password':'Password123!'});assert r.status_code==201
    with app.app_context():
        from models.user import User
        u=User.query.filter_by(email='user@relay.test').first();assert u and u.password_hash != 'Password123!'
    assert client.post('/api/auth/login',json={'email':'user@relay.test','password':'Password123!'}).status_code==200

def test_private_endpoint(client): assert client.get('/api/bookings').status_code==401

def test_resource_permission_and_active(client,app):
    with app.app_context():
        owner=create_user(db,'owner@relay.test','owner');r=add_resource(owner); student=create_user(db,'student@relay.test')
    assert login(client,'student@relay.test').status_code==200
    assert client.get('/api/resources').json['resources'][0]['id']==r.id
    assert client.post('/api/resources',json={'name':'x','category':'x','location':'x'}).status_code==403

def test_booking_and_lifecycle(client,app):
    with app.app_context():
        owner=create_user(db,'owner2@relay.test','owner');student=create_user(db,'student2@relay.test',training='oscilloscope');r=add_resource(owner,training='oscilloscope')
    login(client,'student2@relay.test');start=datetime.utcnow()+timedelta(days=1)
    response=client.post('/api/bookings',json=payload(r,start,start+timedelta(hours=1)));assert response.status_code==201
    bid=response.json['booking']['id']
    client.post('/api/auth/logout');login(client,'owner2@relay.test'); assert client.post(f'/api/bookings/{bid}/approve',json={'reason':'Approved'}).status_code==200
    assert client.post(f'/api/bookings/{bid}/check-in',json={'condition_description':'No damage'}).status_code==200
    with app.app_context(): assert Booking.query.get(bid).condition_reports
    assert client.post(f'/api/bookings/{bid}/return',json={'condition_description':'Returned complete'}).status_code==200

def test_ineligible_waitlist_and_audit(client,app):
    with app.app_context():
        owner=create_user(db,'owner3@relay.test','owner');student=create_user(db,'student3@relay.test');r=add_resource(owner,training='laser-cutter')
    login(client,'student3@relay.test'); res=client.post('/api/bookings',json=payload(r));assert res.status_code==201 and res.json['booking']['status']=='waitlisted'
    with app.app_context(): assert AuditLog.query.count()>=1
    client.post('/api/auth/logout');login(client,'owner3@relay.test');assert client.post(f"/api/bookings/{res.json['booking']['id']}/approve",json={}).status_code==409

def test_conflict_and_invalid_transition(client,app):
    with app.app_context():
        owner=create_user(db,'owner4@relay.test','owner');student=create_user(db,'student4@relay.test');r=add_resource(owner)
    login(client,'student4@relay.test');start=datetime.utcnow()+timedelta(days=2);p=payload(r,start,start+timedelta(hours=2));a=client.post('/api/bookings',json=p).json['booking']['id']
    client.post('/api/auth/logout');login(client,'owner4@relay.test');client.post(f'/api/bookings/{a}/approve',json={'reason':'ok'})
    client.post('/api/auth/logout');login(client,'student4@relay.test');assert client.post('/api/bookings',json=p).status_code==201
    b=client.post('/api/bookings',json=p).json['booking']['id']
    assert client.post(f'/api/bookings/{b}/return',json={'condition_description':'x'}).status_code==409
    assert client.post(f'/api/bookings/{b}/check-in',json={}).status_code==409

def test_incident(client,app):
    with app.app_context():
        admin=create_user(db,'admin@relay.test','admin');student=create_user(db,'student5@relay.test');owner=create_user(db,'owner5@relay.test','owner');r=add_resource(owner)
    login(client,'student5@relay.test');bid=client.post('/api/bookings',json=payload(r)).json['booking']['id'];i=client.post('/api/incidents',json={'booking_id':bid,'description':'Cable damaged'});assert i.status_code==201
    client.post('/api/auth/logout');login(client,'admin@relay.test');iid=i.json['incident']['id'];assert client.post(f'/api/incidents/{iid}/review').status_code==200;assert client.post(f'/api/incidents/{iid}/resolve',json={'resolution_notes':'Human review completed'}).status_code==200

def test_unauthorized_approve(client,app):
    with app.app_context():
        owner=create_user(db,'owner6@relay.test','owner');other=create_user(db,'other@relay.test','owner');student=create_user(db,'student6@relay.test');r=add_resource(owner)
    login(client,'student6@relay.test');bid=client.post('/api/bookings',json=payload(r)).json['booking']['id'];client.post('/api/auth/logout');login(client,'other@relay.test');assert client.post(f'/api/bookings/{bid}/approve').status_code==403
