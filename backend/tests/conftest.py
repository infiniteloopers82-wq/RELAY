import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import pytest
from app import create_app
from extensions import db
@pytest.fixture
def app(tmp_path):
    application=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':f"sqlite:///{tmp_path/'test.db'}",'SECRET_KEY':'test-secret','WTF_CSRF_ENABLED':False})
    with application.app_context():
        db.session.configure(expire_on_commit=False)
        db.drop_all(); db.create_all()
    yield application
@pytest.fixture
def client(app): return app.test_client()
def create_user(db,email,role='student',training='untrained'):
    from models.user import User
    u=User(name=email.split('@')[0],email=email,role=role,training_status=training,institution_status='verified');u.set_password('Password123!');db.session.add(u);db.session.commit();return u
