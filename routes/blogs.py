from routes.blog_form import BlogForm
from flask import Blueprint, request, jsonify, render_template, current_app, url_for, redirect, session, flash, send_from_directory
from models.config import db
from models.blogs import Blog
from routes.category_form import CategoryForm
from models.categories import Category
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


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



blogs_bp = Blueprint('blogs', __name__)

@blogs_bp.route('/blogs', methods=['GET', 'POST'], endpoint='blog_list')
def blogs():
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
    order = request.args.get('order', 'desc', type=str)  # Thêm tham số order

    query = Blog.query
    if search:
        query = query.filter(Blog.title.ilike(f'%{search}%'))
    if category_id:
        query = query.filter(Blog.category_id == category_id)

    # Sắp xếp theo thứ tự tăng dần hoặc giảm dần
    if order == 'asc':
        query = query.order_by(Blog.created_at.asc())
    else:
        query = query.order_by(Blog.created_at.desc())

    blogs = query.paginate(page=page, per_page=per_page, error_out=False)
    blogs_data = []
    for blog in blogs.items:
        blog_dict = blog.to_dict()
        blog_dict['first_image_url'] = extract_first_image_url(blog.content)  # Lấy URL của hình ảnh đầu tiên
        blogs_data.append(blog_dict)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify(blogs=blogs_data, total=blogs.total, pages=blogs.pages, current_page=blogs.page), 200
    else:
        return render_template('admin/blogs.html', categories=categories, blogs=blogs_data, pagination=blogs)



@blogs_bp.route('/blogs/<int:blog_id>', methods=['GET'], endpoint='blog_details')
def blog_details(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog_dict = blog.to_dict()
    blog_dict['first_image_url'] = extract_first_image_url(blog.content)  # Lấy URL của hình ảnh đầu tiên

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify(blog=blog_dict), 200
    else:
        return render_template('admin/blogs_details.html', blog=blog_dict)


@blogs_bp.route('/blogs/new', methods=['GET', 'POST'])
@role_required([1])  # Chỉ cho phép admin truy cập
def blog_create():
    form = BlogForm()
    category_form = CategoryForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user_id = session.get('user_id')
            # Giải mã HTML entities và làm sạch nội dung HTML
            content = unescape(request.form.get('content'))
            clean_content = bleach.clean(content, tags=['p', 'h1', 'h2', 'h3', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'blockquote', 'img', 'a', 'span'], attributes={'img': ['src', 'alt'], 'a': ['href', 'title']})
            
            blog = Blog(
                user_id=current_user_id,
                title=form.title.data,
                content=clean_content,
                category_id=form.category_id.data # Thêm category_id vào đây
            )
            db.session.add(blog)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(message='Blog created successfully!', blog=blog.to_dict()), 201
            else:
                return redirect(url_for('blogs.blog_list'))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(errors=form.errors), 400
    categories = Category.query.all()
    return render_template('admin/blogs_form.html', form=form, category_form=category_form)


@blogs_bp.route('/blogs/edit/<int:blog_id>', methods=['GET', 'POST'])
@role_required([1])  # Chỉ cho phép admin truy cập
def blog_edit(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    form = BlogForm(obj=blog)
    category_form = CategoryForm()  # Thêm dòng này
    
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(blog)
        db.session.commit()
        flash('Blog updated successfully!', 'success')
        return redirect(url_for('blogs.blog_list'))
    
    categories = Category.query.all()
    return render_template('admin/blogs_form.html', form=form, blog=blog, categories=categories, category_form=category_form)


@blogs_bp.route('/blogs/delete/<int:blog_id>', methods=['POST'])
@role_required([1])  # Chỉ cho phép admin xóa blog
def blog_delete(blog_id):
    if request.form.get('_method') == 'DELETE':
        blog = Blog.query.get_or_404(blog_id)
        db.session.delete(blog)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(message='Blog deleted successfully!'), 200
        else:
            return redirect(url_for('blogs.blog_list'))
    return jsonify(message='Method Not Allowed'), 405

@blogs_bp.route('/blog_user', methods=['GET'])
def blog_user():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify(message='User not logged in'), 401
    blogs = Blog.query.filter_by(user_id=current_user_id).all()
    blogs_data = [blog.to_dict() for blog in blogs]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(blogs=blogs_data), 200
    else:
        return render_template('admin/user_blogs.html', blogs=blogs_data)


def extract_first_image_url(content):
    match = re.search(r'<img.*?src=["\'](.*?)["\']', content)
    return match.group(1) if match else None

## @blogs_bp.route('/upload_image', methods=['POST'])
## @role_required([1])  # Chỉ cho phép admin upload hình ảnh
## def upload_image():
 ##     if 'image' not in request.files:
 ###### if relative_path:
  ###  return jsonify(error='Invalid file type'), 400

@blogs_bp.route('/toggle_publish/<int:blog_id>', methods=['POST'])
@login_required
def toggle_publish(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.is_published = not blog.is_published
    db.session.commit()
    return redirect(url_for('blogs.blog_list'))

@blogs_bp.route('/toggle_favorite/<int:blog_id>', methods=['POST'])
@login_required
def toggle_favorite(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.is_favorite = not blog.is_favorite
    db.session.commit()
    return redirect(url_for('blogs.blog_list'))


def get_featured_blogs():
    featured_blogs = Blog.query.filter_by(is_favorite=True, is_published=True).order_by(Blog.created_at.desc()).limit(6).all()
    featured_blogs_data = []
    for blog in featured_blogs:
        blog_dict = blog.to_dict()
        blog_dict['first_image_url'] = extract_first_image_url(blog.content)
        featured_blogs_data.append(blog_dict)
    return featured_blogs_data

@blogs_bp.route('/featured', methods=['GET'])
def featured_blogs():
    featured_blogs = get_featured_blogs()
    return jsonify(featured_blogs=featured_blogs)