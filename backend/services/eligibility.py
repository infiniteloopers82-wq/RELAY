def eligible(user, resource):
    reasons=[]
    required=(resource.training_required or '').strip()
    if required and required.lower() not in [x.strip().lower() for x in (user.training_status or '').split(',')]:
        reasons.append(f'Required training: {required}')
    if resource.access_requirements and 'member' in resource.access_requirements.lower() and not user.institution_status:
        reasons.append('Institution membership is required')
    return len(reasons)==0, reasons
