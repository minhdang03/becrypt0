from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from models.config import db
from models.users import User
from utils.decorators import role_required
from routes.user_form import UserForm
import logging
from flask_paginate import Pagination, get_page_parameter  # Đảm bảo nhập khẩu đúng
from flask_login import login_required
from flask_login import current_user
from models.blogs import Blog

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)

@users_bp.route('/', methods=['GET'])
@role_required([1])  # Chỉ cho phép admin truy cập
def manage_users():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    logger.info("Fetching all users from the database")
    
    # Lấy số trang hiện tại từ query string, mặc định là trang 1
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5  # Số lượng hàng hiển thị trên mỗi trang
    
    # Truy vấn dữ liệu người dùng và sắp xếp theo user_id
    users_query = User.query.order_by(User.user_id)
    pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    users_data = [user.to_dict() for user in users]
    logger.info(f"Fetched {len(users_data)} users on page {page}")

    pagination = Pagination(page=page, total=pagination.total, per_page=per_page, css_framework='bootstrap4')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Kiểm tra nếu yêu cầu là AJAX
        return jsonify(users=users_data), 200
    else:
        return render_template('admin/users.html', users=users, pagination=pagination)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@role_required([1])  # Chỉ cho phép admin xóa người dùng
def delete_user(user_id):
    if request.form.get('_method') == 'DELETE':
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(message='User deleted successfully!'), 200
        else:
            return redirect(url_for('users.manage_users'))
    return jsonify(message='Method Not Allowed'), 405

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@role_required([1])  # Chỉ cho phép admin chỉnh sửa người dùng
def edit_user(user_id):
    logger.info(f"Fetching user with ID: {user_id}")
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if request.method == 'POST':
        logger.info("Received POST request")
        if form.validate_on_submit():
            logger.info("Form validated successfully")
            user.fullname = form.fullname.data
            user.email = form.email.data
            user.role_id = form.role_id.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            logger.info(f"User with ID: {user_id} updated successfully")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(message='User updated successfully!', user=user.to_dict()), 200
            else:
                return redirect(url_for('users.manage_users'))
        else:
            logger.warning("Form validation failed")
            logger.warning(f"Form errors: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(errors=form.errors), 400
    return render_template('admin/user_form.html', form=form, user=user)

@users_bp.route('/reset_password/<int:user_id>', methods=['POST'])
@role_required([1])  # Chỉ cho phép admin đặt lại mật khẩu
def reset_password(user_id):
    logger.info(f"Resetting password for user with ID: {user_id}")
    user = User.query.get_or_404(user_id)
    old_password_hash = user.password  # Sử dụng thuộc tính password
    user.set_password('123456')  # Đặt mật khẩu mới và mã hóa
    db.session.commit()
    new_password_hash = user.password  # Sử dụng thuộc tính password
    logger.info(f"Old password hash: {old_password_hash}")
    logger.info(f"New password hash: {new_password_hash}")
    if old_password_hash == new_password_hash:
        logger.error("Password hash did not change!")
    else:
        logger.info("Password hash updated successfully.")
    flash('Password has been reset successfully.', 'success')
    return redirect(url_for('users.manage_users'))

@users_bp.route('/profile')
@login_required
@role_required([1,2,3])
def profile():
    # Thay đổi current_user.id thành current_user.user_id
    user_blogs = Blog.query.filter_by(user_id=current_user.user_id).order_by(Blog.created_at.desc()).limit(5).all()
    return render_template('profile.html', user_blogs=user_blogs)