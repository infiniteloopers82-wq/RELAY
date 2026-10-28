from flask import Blueprint,request,jsonify
from extensions import db
from models.resource import Resource
from routes.auth import login_required,current_user,roles
from services.audit_service import audit
bp=Blueprint('resources',__name__,url_prefix='/api/resources')

@bp.get('')
def list_resources():
    q=Resource.query.filter_by(active=True)
    category=request.args.get('category'); search=request.args.get('search')
    if category: q=q.filter(Resource.category.ilike(f'%{category}%'))
    if search: q=q.filter(db.or_(Resource.name.ilike(f'%{search}%'),Resource.description.ilike(f'%{search}%')))
    return jsonify({'resources':[r.to_dict() for r in q.order_by(Resource.name).all()]})

@bp.get('/<int:id>')
def detail(id):
    r=db.session.get(Resource,id)
    return jsonify({'resource':r.to_dict()}) if r else (jsonify({'error':'Resource not found','code':'not_found'}),404)

@bp.post('')
@login_required
def create_resource():
    u=current_user()
    if u.role not in ('owner','admin'): return jsonify({'error':'Owner permission required','code':'forbidden'}),403
    d=request.get_json(silent=True) or {}
    if not all(d.get(k) for k in ('name','category','location')): return jsonify({'error':'name, category and location are required','code':'validation_error'}),400
    r=Resource(name=d['name'],description=d.get('description',''),category=d['category'],location=d['location'],owner_id=u.id,availability=d.get('availability','Mon–Fri, 9:00–18:00'),access_requirements=d.get('access_requirements',''),training_required=d.get('training_required',''),supervision_required=bool(d.get('supervision_required')),usage_limit=int(d.get('usage_limit',3)),active=bool(d.get('active',True)))
    db.session.add(r); db.session.flush(); audit(u,'resource_created','resource',r.id); db.session.commit()
    return jsonify({'resource':r.to_dict()}),201

@bp.put('/<int:id>')
@login_required
def update_resource(id):
    r=db.session.get(Resource,id); u=current_user()
    if not r: return jsonify({'error':'Resource not found','code':'not_found'}),404
    if u.role!='admin' and r.owner_id!=u.id: return jsonify({'error':'Owner permission required','code':'forbidden'}),403
    d=request.get_json(silent=True) or {}
    for key in ('name','description','category','location','availability','access_requirements','training_required','usage_limit'):
        if key in d: setattr(r,key,d[key])
    if 'supervision_required' in d: r.supervision_required=bool(d['supervision_required'])
    if 'active' in d: r.active=bool(d['active'])
    audit(u,'resource_updated','resource',r.id); db.session.commit(); return jsonify({'resource':r.to_dict()})

@bp.delete('/<int:id>')
@login_required
def delete_resource(id):
    r=db.session.get(Resource,id); u=current_user()
    if not r: return jsonify({'error':'Resource not found','code':'not_found'}),404
    if u.role!='admin' and r.owner_id!=u.id: return jsonify({'error':'Owner permission required','code':'forbidden'}),403
    r.active=False; audit(u,'resource_deactivated','resource',r.id); db.session.commit(); return jsonify({'message':'Resource deactivated; history preserved'})
