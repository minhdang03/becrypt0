from routes.blog_form import BlogForm
from flask import Blueprint, request, jsonify, render_template, current_app, url_for, redirect, session, flash, send_from_directory
from models.config import db
from models.blogs import Blog
from routes.category_form import CategoryForm
from models.categories import Category
from models.blog_images_model import BlogImage
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from utils.decorators import role_required
from werkzeug.utils import secure_filename  # Thay đổi import từ flask sang werkzeug
import logging
import os
import bleach
from html import unescape
import uuid
import re
from flask_login import login_required
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import shutil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_temp_images():
    temp_folder = os.path.join(current_app.static_folder, 'img', 'blogs', 'temp')
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_temp_images, trigger="interval", minutes=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

def get_image_url(relative_path):
    return url_for('static', filename=relative_path, _external=True)


blogs_user_bp = Blueprint('blogs_user', __name__)

@blogs_user_bp.route('/', methods=['GET', 'POST'], endpoint='blog_list')
def blogs_list():
    if request.method == 'POST':
        # Xử lý POST request nếu cần
        pass

    # Truy vấn tất cả các danh mục từ cơ sở dữ liệu
    categories = Category.query.all()

    # Xử lý GET request
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Số lượng blog mỗi trang
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category', None, type=int)

    query = Blog.query
    if search:
        query = query.filter(Blog.title.ilike(f'%{search}%'))
    if category_id:
        query = query.filter(Blog.category_id == category_id)

    blogs = query.paginate(page=page, per_page=per_page, error_out=False)
    blogs_data = []
    for blog in blogs.items:
        blog_dict = blog.to_dict()
        blog_dict['first_image_url'] = extract_first_image_url(blog.content)  # Lấy URL của hình ảnh đầu tiên
        blogs_data.append(blog_dict)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify(blogs=blogs_data, total=blogs.total, pages=blogs.pages, current_page=blogs.page), 200
    else:
        return render_template('blogs_user_list.html', categories=categories, blogs=blogs_data, pagination=blogs)



#@blogs_user_bp.route('/<int:blog_id>', methods=['GET'], endpoint='blog_details')
# def blog_details(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog_dict = blog.to_dict()
    blog_dict['first_image_url'] = extract_first_image_url(blog.content)  # Lấy URL của hình ảnh đầu tiên

    # Xử lý các đường dẫn hình ảnh trong nội dung blog
    soup = BeautifulSoup(blog.content, 'html.parser')
    images = soup.find_all('img')

    if len(images) == 1:
        # Nếu chỉ có một hình ảnh, loại bỏ thẻ <img>
        images[0].decompose()
    else:
        for img in images:
            src = img.get('src')
            if not src.startswith('http'):
                # Loại bỏ phần tiền tố dư thừa nếu có
                if src.startswith('/blogs_user/'):
                    src = src[len('/blogs_user/'):]
                # Thêm tiền tố /static/img/blogs nếu thiếu
                if not src.startswith('static/img/blogs/'):
                    src = f"static/img/blogs/{src.lstrip('/')}"
                img['src'] = f"{os.getenv('DOMAIN')}/{src.lstrip('/')}"

    blog_dict['content'] = str(soup)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify(blog=blog_dict), 200
    else:
        return render_template('blogs_user_details.html', blog=blog_dict)
    
@blogs_user_bp.route('/<int:blog_id>', methods=['GET'], endpoint='blog_details')
def blog_details(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog_dict = blog.to_dict()
    blog_dict['first_image_url'] = extract_first_image_url(blog.content)  # Lấy URL của hình ảnh đầu tiên

    # Xử lý các đường dẫn hình ảnh trong nội dung blog
    soup = BeautifulSoup(blog.content, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src.startswith('http'):
            # Loại bỏ phần tiền tố dư thừa nếu có
            if src.startswith('/blogs_user/'):
                src = src[len('/blogs_user/'):]
            # Thêm tiền tố /static/img/blogs nếu thiếu
            if not src.startswith('static/img/blogs/'):
                src = f"static/img/blogs/{src.lstrip('/')}"
            img['src'] = f"{os.getenv('DOMAIN')}/{src.lstrip('/')}"
    blog_dict['content'] = str(soup)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify(blog=blog_dict), 200
    else:
        return render_template('blogs_user_details.html', blog=blog_dict)

@blogs_user_bp.route('/new', methods=['GET', 'POST'])
def blog_create():
    print("All form data:", request.form.to_dict())
    print("Files:", request.files)
    form = BlogForm()
    category_form = CategoryForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user_id = session.get('user_id')
            content = unescape(request.form.get('content'))
            clean_content = bleach.clean(content, tags=['p', 'h1', 'h2', 'h3', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'blockquote', 'img', 'a', 'span'], attributes={'img': ['src', 'alt'], 'a': ['href', 'title']})
            thumbnail_url = request.form.get('thumbnail_url')
            print(f"Received thumbnail_url: {thumbnail_url}")  # Debug print
           
            # Move thumbnail image from temp to static/img/blogs/thumbnails
            if thumbnail_url and 'temp' in thumbnail_url:
                filename = os.path.basename(thumbnail_url)
                temp_path = os.path.join(current_app.root_path, 'static/img/blogs/temp', filename)
                new_path = os.path.join(current_app.root_path, 'static/img/blogs/thumbnails', filename)
                shutil.move(temp_path, new_path)
                thumbnail_url = f'static/img/blogs/thumbnails/{filename}'
                print(f"Moved thumbnail to: {thumbnail_url}")  # Debug print

            blog = Blog(
                user_id=current_user_id,
                title=form.title.data,
                content=clean_content,
                category_id=form.category_id.data,
                thumbnail_url=thumbnail_url
            )
            db.session.add(blog)
            db.session.commit()
            print(f"Saved blog thumbnail_url: {blog.thumbnail_url}")  # Debug print
            
            # Lưu hình ảnh từ nội dung blog
            soup = BeautifulSoup(clean_content, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src')
                if 'temp' in src:
                    filename = os.path.basename(src)
                    temp_path = os.path.join(current_app.static_folder, 'img', 'blogs', 'temp', filename)
                    new_path = os.path.join(current_app.static_folder, 'img', 'blogs', filename)
                    os.rename(temp_path, new_path)
                    relative_path = f'static/img/blogs/{filename}'
                    img['src'] = relative_path  # Lưu đường dẫn tương đối
                    blog_image = BlogImage(blog_id=blog.blog_id, image_url=relative_path)
                    db.session.add(blog_image)
                else:
                    # Đảm bảo rằng các đường dẫn hình ảnh có tiền tố 'static/img/blogs/'
                    if not src.startswith('static/img/blogs/'):
                        img['src'] = f'static/img/blogs/{src.lstrip("/")}'
            
            # Update blog content with new image paths
            blog.content = str(soup)
            db.session.commit()            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(message='Blog created successfully!', blog=blog.to_dict()), 201
            else:
                # Lấy URL của bài viết mới
                blog_url = url_for('blogs_user.blog_details', blog_id=blog.blog_id)

                # Chuyển hướng đến bài viết mới
                return redirect(blog_url)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(errors=form.errors), 400

    categories = Category.query.all()
    return render_template('blogs_user_forms.html', form=form, category_form=category_form)



@blogs_user_bp.route('/user_upload_image', methods=['POST'])
def upload_image():
    if 'images' not in request.files:
        return jsonify(error='No image files'), 400
    
    files = request.files.getlist('images')
    if not files:
        return jsonify(error='No image files'), 400
    
    image_urls = []
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
                file_path = os.path.join(current_app.static_folder, 'img', 'blogs', 'temp', filename)
                
                # Tạo thư mục nếu chưa tồn tại
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                image_url = url_for('static', filename=f'img/blogs/temp/{filename}', _external=True)
                image_urls.append(image_url)
            except Exception as e:
                return jsonify(error=f'Failed to save file: {str(e)}'), 500
        else:
            return jsonify(error=f'Invalid file type: {file.filename}'), 400
    
    return jsonify(urls=image_urls), 200

@blogs_user_bp.route('/upload-thumbnailurl-temp', methods=['POST'])
def upload_thumbnailurl_temp():
    if 'thumbnail_url' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['thumbnail_url']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.static_folder, 'img', 'blogs', 'temp', filename)
        file.save(temp_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'File upload failed'}), 500

@blogs_user_bp.route('/edit/<int:blog_id>', methods=['GET', 'POST'])
def blog_edit(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    form = BlogForm(obj=blog)
    category_form = CategoryForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            current_user_id = session.get('user_id')
            content = unescape(request.form.get('content'))
            clean_content = bleach.clean(content, tags=['p', 'h1', 'h2', 'h3', 'h4', 'sup', 'a', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'blockquote', 'img', 'span'], attributes={'img': ['src', 'alt'], 'a': ['href', 'title']})
            
            blog.title = form.title.data
            blog.content = clean_content
            blog.category_id = form.category_id.data
            
            # Lưu hình ảnh từ nội dung blog
            soup = BeautifulSoup(clean_content, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src')
                if 'temp' in src:
                    filename = os.path.basename(src)
                    temp_path = os.path.join(current_app.static_folder, 'img', 'blogs', 'temp', filename)
                    new_path = os.path.join(current_app.static_folder, 'img', 'blogs', filename)
                    os.rename(temp_path, new_path)
                    relative_path = f'static/img/blogs/{filename}'
                    img['src'] = relative_path  # Lưu đường dẫn tương đối
                    blog_image = BlogImage(blog_id=blog.blog_id, image_url=relative_path)
                    db.session.add(blog_image)
                else:
                    # Đảm bảo rằng các đường dẫn hình ảnh không có tiền tố dư thừa
                    if src.startswith('/blogs_user/edit/'):
                        src = src.replace('/blogs_user/edit/', '/')
                    img['src'] = src
            
            # Cập nhật lại nội dung blog với đường dẫn hình ảnh mới
            blog.content = str(soup)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(message='Blog updated successfully!', blog=blog.to_dict()), 200
            else:
                return redirect(url_for('blogs_user.blog_list'))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(errors=form.errors), 400

    categories = Category.query.all()
    return render_template('blogs_user_form.html', form=form, category_form=category_form, blog=blog)

@blogs_user_bp.route('/delete/<int:blog_id>', methods=['POST'])
def blog_delete(blog_id):
    if request.form.get('_method') == 'DELETE':
        blog = Blog.query.get_or_404(blog_id)
        
        # Tìm và xóa các hình ảnh liên quan từ cơ sở dữ liệu
        blog_images = BlogImage.query.filter_by(blog_id=blog_id).all()
        for blog_image in blog_images:
            # Xóa tệp hình ảnh từ hệ thống tệp
            image_path = os.path.join(current_app.static_folder, blog_image.image_url)
            if os.path.exists(image_path):
                os.remove(image_path)
            db.session.delete(blog_image)
        
        db.session.delete(blog)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(message='Blog deleted successfully!'), 200
        else:
            return redirect(url_for('blogs_user.blog_list'))
    return jsonify(message='Method Not Allowed'), 405

@blogs_user_bp.route('/user_blogs', methods=['GET'])
def blog_user():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify(message='User not logged in'), 401
    blogs = Blog.query.filter_by(user_id=current_user_id).all()
    blogs_data = [blog.to_dict() for blog in blogs]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(blogs=blogs_data), 200
    else:
        return render_template('user_blogs.html', blogs=blogs_data)


def extract_first_image_url(content):
    soup = BeautifulSoup(content, 'html.parser')
    img = soup.find('img')
    if img and 'src' in img.attrs:
        src = img['src']
        if not src.startswith('http'):
            # Loại bỏ phần tiền tố dư thừa nếu có
            if src.startswith('/blogs_user/'):
                src = src[len('/blogs_user/'):]
            src = f"{os.getenv('DOMAIN')}/{src.lstrip('/')}"
        return src
    return None


@blogs_user_bp.route('/featured', methods=['GET'])
def featured_blogs():
    featured = Blog.query.order_by(Blog.created_at.desc()).limit(6).all()
    featured_data = []
    for blog in featured:
        blog_dict = blog.to_dict()
        blog_dict['first_image_url'] = extract_first_image_url(blog.content)
        featured_data.append(blog_dict)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify(featured_blogs=featured_data), 200
    else:
        return render_template('featured.html', featured_blogs=featured_data)

@blogs_user_bp.route('/discard_blog', methods=['POST'])
def discard_blog():
    # Xóa các hình ảnh tạm thời khi người dùng hủy bỏ việc tạo blog
    delete_temp_images()
    return jsonify(message='Temporary images deleted'), 200

@blogs_user_bp.route('/home', methods=['GET'])
def home():
    featured_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(6).all()
    featured_data = []
    for blog in featured_blogs:
        blog_dict = blog.to_dict()
        blog_dict['image_url'] = extract_first_image_url(blog.content)
        featured_data.append(blog_dict)
    
    recent_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(4).all()
    recent_data = []
    for blog in recent_blogs:
        blog_dict = blog.to_dict()
        blog_dict['image_url'] = extract_first_image_url(blog.content)
        recent_data.append(blog_dict)
    
    print("Featured blogs:", featured_data)  # Thêm log
    print("Recent blogs:", recent_data)  # Thêm log
    
    return render_template('index.html', featured_blogs=featured_data, blogs=recent_data)

@blogs_user_bp.route('/get_existing_images', methods=['GET'])
def get_existing_images():
    try:
        # Truy vấn tất cả các hình ảnh từ cơ sở dữ liệu
        images = BlogImage.query.all()
        image_urls = [get_image_url(image.image_url) for image in images]
        return jsonify(urls=image_urls), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
    