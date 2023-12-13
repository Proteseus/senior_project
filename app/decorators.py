from functools import wraps
from flask_login import current_user

def org_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return {'message': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated_function

def sys_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return {'message': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated_function
