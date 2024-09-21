from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role_id' not in session:
                flash("Bạn cần đăng nhập để truy cập trang này.")
                return redirect(url_for('auth.login'))
            
            if session['role_id'] not in allowed_roles:
                flash("Bạn không có quyền truy cập trang này.")
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator