from flask import Blueprint, jsonify, render_template, request, current_app, url_for, flash, redirect
import requests
import os
import re
import random
import math
from flask_login import login_required
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from models.slideshowimage import SlideshowImage
from models.config import db
from urllib.parse import urlparse, urlunparse
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf

slideshow_bp = Blueprint('slideshow', __name__)

def get_image_folder():
    return os.path.join(current_app.root_path, 'static', 'img', 'slideshow')

def save_image(url, alt_text, is_firstimageblogs=False):
    # Lưu đường dẫn hình ảnh vào cơ sở dữ liệu
    new_image = SlideshowImage(url=url, alt_text=alt_text, is_firstimageblogs=is_firstimageblogs)
    db.session.add(new_image)
    db.session.commit()
    return new_image.id

def delete_image(image_name):
    image_folder = get_image_folder()
    filepath = os.path.join(image_folder, image_name)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def get_nasa_images():
    url = "https://science.nasa.gov/gallery/universe-images/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    images = []
    
    # Get existing image URLs from the database
    existing_images = {image.url for image in SlideshowImage.query.all()}
    
    for img in soup.find_all('img'):
        src = img.get('src')
        alt = img.get('alt')
        if src and ('wp-content/uploads' in src or 'images.nasa.gov' in src):
            if not src.startswith('http'):
                src = 'https://science.nasa.gov' + src
            if src not in existing_images:
                images.append({
                    'src': src,
                    'alt': alt or 'NASA Universe Image'
                })
    return images

@slideshow_bp.route('/random_images', methods=['GET'])
def get_random_images():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    # Lấy tất cả hình ảnh từ NASA
    all_images = get_nasa_images()
    
    # Xáo trộn danh sách hình ảnh
    random.shuffle(all_images)
    
    # Tính toán tổng số trang
    total_pages = math.ceil(len(all_images) / per_page)
    
    # Tính toán start và end index cho trang hiện tại
    start = (page - 1) * per_page
    end = start + per_page
    
    # Lấy hình ảnh cho trang hiện tại
    page_images = all_images[start:end]
    
    return jsonify({
        'images': page_images,
        'total_pages': total_pages
    })

@slideshow_bp.route('/manage_images')
@login_required
def manage_images():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Số lượng hình ảnh mỗi trang
    
    # Sắp xếp theo cột is_firstimageblogs với giá trị True trước
    images_query = SlideshowImage.query.order_by(SlideshowImage.is_firstimageblogs.desc()).paginate(page=page, per_page=per_page, error_out=True)
    images = images_query.items
    total_pages = images_query.pages
    
    return render_template('admin/imageNasa.html', 
                           images=images, 
                           current_page=page, 
                           total_pages=total_pages,
                           per_page=per_page)

@slideshow_bp.route('/save_images', methods=['POST'])
@login_required
def save_images():
    data = request.json
    image_data = data.get('images', [])
    
    print(f"Received image data: {image_data}")  # Thêm câu lệnh in ra để kiểm tra

    saved_images = []
    for image in image_data:
        try:
            # Parse the URL and remove the query string
            parsed_url = urlparse(image['src'])
            clean_url = urlunparse(parsed_url._replace(query=''))
            
            alt_text = image['alt']
            is_firstimageblogs = image.get('is_firstimageblogs', False)
            image_id = save_image(clean_url, alt_text, is_firstimageblogs)
            if image_id:
                saved_images.append(image_id)
        except Exception as e:
            print(f"Error saving image {image['src']}: {e}")
    
    return jsonify({
        'message': f'Đã lưu {len(saved_images)} hình ảnh thành công',
        'saved_images': saved_images
    })
    
@slideshow_bp.route('/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = SlideshowImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Hình ảnh đã được xóa thành công.', 'success')
    return redirect(url_for('slideshow.manage_images'))

@slideshow_bp.route('/add_nasa_images', methods=['GET'])
@login_required
def add_nasa_images():
    return render_template('admin/imageNasa_add.html')

@slideshow_bp.route('/get_images')
def get_images():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    images_query = SlideshowImage.query.paginate(page=page, per_page=per_page, error_out=False)
    images = images_query.items
    total_pages = images_query.pages
    
    return jsonify({
        'images': [{'url': image.url, 'alt_text': image.alt_text, 'is_firstimageblogs': image.is_firstimageblogs} for image in images],
        'total_pages': total_pages,
        'current_page': page
    })

@slideshow_bp.route('/get_random_image')
def get_random_image():
    images = SlideshowImage.query.all()
    if not images:
        return jsonify({'error': 'No images found'}), 404
    
    random_image = random.choice(images)
    
    return jsonify({
        'url': random_image.url,
        'alt_text': random_image.alt_text,
        'is_firstimageblogs': random_image.is_firstimageblogs
    })

@slideshow_bp.route('/get_mot_image', methods=['GET'])
def get_mot_image():
    # Lấy tất cả các URL hình ảnh từ cơ sở dữ liệu với is_firstimageblogs = True
    images = SlideshowImage.query.filter_by(is_firstimageblogs=True).all()
    
    if not images:
        return jsonify({'error': 'Không tìm thấy hình ảnh'}), 404
    
    # Chọn ngẫu nhiên một URL hình ảnh
    random_image = random.choice(images)
    
    return jsonify({
        'url': random_image.url,
        'is_firstimageblogs': random_image.is_firstimageblogs
    })

@slideshow_bp.route('/toggle_first_image/<int:image_id>', methods=['POST'])
@login_required
def toggle_first_image(image_id):
    image = SlideshowImage.query.get_or_404(image_id)
    image.is_firstimageblogs = not image.is_firstimageblogs
    db.session.commit()
    return jsonify({'success': True})

@slideshow_bp.route('/get_background_image', methods=['GET'])
def get_background_image():
    # Lấy một hình ảnh có is_firstimageblogs là False
    image = SlideshowImage.query.filter_by(is_firstimageblogs=False).first()
    
    if not image:
        return jsonify({'error': 'Không tìm thấy hình ảnh'}), 404
    
    return jsonify({'url': image.url})