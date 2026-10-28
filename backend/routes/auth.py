from functools import wraps
from flask import Blueprint,request,jsonify,session
from extensions import db
from models.user import User
from services.audit_service import audit
bp=Blueprint('auth',__name__,url_prefix='/api/auth')

def current_user():
    uid=session.get('user_id'); return db.session.get(User,uid) if uid else None

def login_required(fn):
    @wraps(fn)
    def wrapped(*args,**kwargs):
        if not current_user(): return jsonify({'error':'Authentication required','code':'unauthenticated'}),401
        return fn(*args,**kwargs)
    return wrapped

def roles(*allowed):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args,**kwargs):
            u=current_user()
            if not u or u.role not in allowed: return jsonify({'error':'You do not have permission for this action','code':'forbidden'}),403
            return fn(*args,**kwargs)
        return wrapped
    return decorator

@bp.post('/register')
def register():
    d=request.get_json(silent=True) or {}; required=['name','email','password']
    missing=[x for x in required if not d.get(x)]
    if missing: return jsonify({'error':'Missing required fields','code':'validation_error','fields':missing}),400
    email=d['email'].strip().lower()
    if User.query.filter_by(email=email).first(): return jsonify({'error':'Email is already registered','code':'duplicate'}),409
    u=User(name=d['name'].strip(),email=email,role='student',institution_status=d.get('institution_status'),training_status=d.get('training_status','untrained')); u.set_password(d['password'])
    db.session.add(u); db.session.flush(); audit(u,'user_registered','user',u.id)
    db.session.commit(); session['user_id']=u.id
    return jsonify({'user':u.to_dict()}),201

@bp.post('/login')
def login():
    d=request.get_json(silent=True) or {}
    u=User.query.filter_by(email=(d.get('email') or '').strip().lower()).first()
    if not u or not u.check_password(d.get('password','')): return jsonify({'error':'Invalid email or password','code':'invalid_credentials'}),401
    session['user_id']=u.id
    audit(u,'user_login','user',u.id); db.session.commit()
    return jsonify({'user':u.to_dict()})

@bp.get('/me')
@login_required
def me(): return jsonify({'user':current_user().to_dict()})

@bp.post('/logout')
def logout(): session.clear(); return jsonify({'message':'Logged out'})
