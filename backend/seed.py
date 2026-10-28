from app import create_app
from extensions import db
from models import User,Resource
from datetime import datetime
app=create_app()
with app.app_context():
    if User.query.count(): print('Seed skipped: users already exist. Use a fresh relay.db for demo reset.')
    else:
        people=[('student','student@relay.demo','Demo Student','verified','oscilloscope,3d-printer'),('trainready','trained@relay.demo','Trained Student','verified','laser-cutter'),('untrained','untrained@relay.demo','Untrained Student','verified','untrained'),('owner','owner@relay.demo','Demo Owner','staff','staff'),('admin','admin@relay.demo','Demo Admin','staff','staff')]
        users={}
        for role,email,name,status,training in people:
            u=User(name=name,email=email,role=role,institution_status=status,training_status=training); u.set_password('Relay123!'); db.session.add(u); users[role]=u
        db.session.flush()
        owner=users['owner']
        resources=[
        ('Digital Oscilloscope','Four-channel bench oscilloscope','Electronics','Engineering Lab A','oscilloscope'),('3D Printer – MakerBot','Fused filament fabrication printer','Fabrication','Innovation Workshop','3d-printer'),('DSLR Camera Kit','Camera, tripod and two lenses','Media','Media Resource Room',''),('Laser Cutter','60W enclosed laser cutter','Fabrication','Innovation Workshop','laser-cutter'),('Project Robotics Kit','Sensors, motors and controller boards','Electronics','Robotics Lab','robotics'),('Microscopy Suite','Compound microscope and imaging camera','Laboratory','Biology Lab','lab-safety'),('Podcast Studio','Sound booth with four microphones','Media','Creative Hub',''),('Workshop Power Tools','Drill, saw and measurement set','Workshop','Central Workshop','workshop-safety'),('Quiet Project Room','Four-seat reservable collaboration room','Spaces','Library Level 2',''),('Soldering Station','Temperature-controlled soldering bench','Electronics','Engineering Lab B','electronics'),
        ]
        for name,desc,cat,loc,training in resources: db.session.add(Resource(name=name,description=desc,category=cat,location=loc,owner_id=owner.id,availability='Mon–Fri, 09:00–18:00',training_required=training,active=True,usage_limit=3))
        db.session.commit(); print('Demo database seeded.')
