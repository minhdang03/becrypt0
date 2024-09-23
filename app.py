from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, g
from flask_cors import CORS
from flask_session import Session
from routes.crypto import crypto_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.blogs import blogs_bp
from routes.admin import admin_bp
from routes.users import users_bp
from routes.category import categories_bp
from models.config import init_app, db
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models.users import User
from flask_caching import Cache
from routes.blogs import get_featured_blogs
from routes.slideshow import slideshow_bp
from routes.blogs_user import blogs_user_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    app.static_folder = 'static'
    app.config['UPLOAD_IMG_FOLDER'] = os.path.join(app.root_path, 'static', 'img')
    app.config['UPLOAD_BLOG_FOLDER'] = os.path.join(app.root_path, 'static', 'img', 'blogs')
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    DOMAIN = os.environ.get('DOMAIN', '127.0.0.1:9999')
    def fix_image_urls(image_path):
        if image_path.startswith('img/'):
            return url_for('static', filename=image_path)
        return image_path
    app.jinja_env.filters['fix_image_urls'] = fix_image_urls
    # Cấu hình CORS
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", 'https://imm0rtal.vercel.app', 'https://sinnhhatvuive.net'],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }})

    # Cấu hình session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')

    Session(app)

    # Khởi tạo cấu hình cơ sở dữ liệu
    init_app(app)
    # Cấu hình JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key')
    jwt = JWTManager(app)

    # Đăng ký blueprint
    app.register_blueprint(crypto_bp, url_prefix='/crypto')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blogs_bp, url_prefix='/blogs')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(slideshow_bp, url_prefix='/slideshow')
    app.register_blueprint(blogs_user_bp, url_prefix='/blogs_user')

    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000', 'https://imm0rtal.vercel.app', 'https://sinnhhatvuive.net']:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    login_manager = LoginManager()
    login_manager.init_app(app)  # Cấu hình LoginManager với app
    login_manager.login_view = 'auth.login'  # Trang login mặc định
    login_manager.login_message = 'You need to login to access this page.'  # Thông báo yêu cầu đăng nhập

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Hàm load user từ database
    
    @app.before_request
    def before_request():
        g.user = current_user  # Sử dụng current_user từ flask_login

    @app.route('/')
    def index():
        featured_blogs = get_featured_blogs()
        return render_template('index.html', featured_blogs=featured_blogs)
    
    @app.route('/about')
    def about():
        return render_template('about.html')


    @app.route('/protected')
    @login_required
    def protected():
        return 'This is a protected page'
    
    @app.context_processor
    def inject_domain():
        return dict(domain=os.getenv('DOMAIN'))
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True)