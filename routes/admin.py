from flask import Blueprint, render_template, redirect, url_for, session
from models.config import db
from models.users import User
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET'])
@role_required([1])  # Chỉ cho phép admin truy cập
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/users', methods=['GET'])
@role_required([1])  # Chỉ cho phép admin truy cập
def manage_users():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)