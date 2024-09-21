from datetime import timedelta
from flask import Blueprint, app, request, jsonify, session, redirect, url_for, render_template, g
from werkzeug.security import generate_password_hash, check_password_hash
from models.config import db
from models.users import User, Role
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt_identity 
from flask import current_app
from flask_login import login_user, logout_user
from routes.user_form import UserForm, RegisterForm
from flask import flash

import logging
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        user = User.query.get(user_id)
        if user:
            g.user = user
        else:
            g.user = None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        fullname = form.fullname.data
        role_id = 3  # Mặc định là 3 (User) nếu không có role_id

        if User.query.filter_by(username=username).first():
            error_message = 'Tên người dùng đã tồn tại'
            return jsonify({'message': error_message}), 400 if request.is_json else render_template('register.html', form=form, error=error_message, user=g.user)

        if User.query.filter_by(email=email).first():
            error_message = 'Email đã tồn tại'
            return jsonify({'message': error_message}), 400 if request.is_json else render_template('register.html', form=form, error=error_message, user=g.user)

        role = Role.query.get(role_id)
        if not role:
            error_message = 'role_id không hợp lệ'
            return jsonify({'message': error_message}), 400 if request.is_json else render_template('register.html', form=form, error=error_message, user=g.user)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, fullname=fullname, role_id=role_id)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            success_message = 'Đăng ký thành công'
            if request.is_json:
                return jsonify({'message': success_message, 'user_id': new_user.user_id}), 201
            else:
                flash(success_message, 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Lỗi trong quá trình đăng ký người dùng: {str(e)}")
            error_message = 'Đã xảy ra lỗi trong quá trình đăng ký'
            return jsonify({'message': error_message}), 500 if request.is_json else render_template('register.html', form=form, error=error_message, user=g.user)
    else:
        return render_template('register.html', form=form, user=g.user)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Login route accessed")
    form = UserForm()  # Tạo instance của LoginForm
    if request.method == 'POST':
        logger.info("POST request received for login")
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            remember_me = data.get('rememberMe', False)
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            remember_me = request.form.get('rememberMe', False)
        
        logger.info(f"Login attempt for username: {username}")
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember_me)
            logger.info(f"User {username} authenticated successfully")
            session['username'] = user.username
            session['full_name'] = user.fullname
            session['role_id'] = user.role.role_id
            session['role_name'] = user.role.role_name if user.role else 'No role assigned'

            if remember_me:
                session.permanent = True
                session_lifetime = timedelta(days=7)
            else:
                session.permanent = False
                session_lifetime = timedelta(minutes=60)

            session.modified = True
            current_app.permanent_session_lifetime = session_lifetime
            
            logger.info(f"Session created for user {username}: {session}")

            if request.is_json:
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'fullname': user.fullname,
                        'role': user.role.role_name
                    },
                    'message': f'Đăng nhập thành công. Phiên sẽ được lưu trong {session_lifetime}.'
                }), 200 
            else:
                logger.info(f"Redirecting user {username} to admin dashboard")
                return redirect(url_for('index'))  # Chuyển hướng đến route 'index'
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            if request.is_json:
                return jsonify({'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng'}), 401
            else:
                return render_template('login.html', form=form, error='Tên đăng nhập hoặc mật khẩu không đúng', user=g.user)

    logger.info("Rendering login template")
    return render_template('login.html', form=form, user=g.user)

@auth_bp.route('/verify-session', methods=['GET'])
def verify_session():
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Request cookies: {request.cookies}")
    logger.info(f"Current session: {session}")
    user_id = session.get('user_id')
    logger.info(f"Verifying session for user_id: {user_id}")
    logger.info(f"Session data: {session}")
    if user_id:
        user = User.query.get(user_id)
        if user:
            logger.info(f"User found: {user.username}")
            return jsonify({
                'valid': True,
                'user': {
                    'id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'fullname': user.fullname,
                    'role': user.role.role_name
                }
            }), 200
    logger.info("No valid session found")
    return jsonify({'valid': False}), 200

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.context_processor
def inject_user():
    return dict(user=g.user)