from flask import Blueprint, jsonify, render_template, request, current_app
import requests
import os
import re
import hashlib
from flask_login import login_required
import os
import re
import random
import math
from bs4 import BeautifulSoup



slideshow_bp = Blueprint('slideshow', __name__)

def get_existing_image_alts():
    image_folder = os.path.join(current_app.static_folder, 'img', 'slideshow')
    existing_images = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    existing_alts = [re.sub(r'_[a-f0-9]{8}\.png$', '', f).replace('_', ' ') for f in existing_images]
    return set(existing_alts)

def get_nasa_images():
    url = "https://science.nasa.gov/gallery/universe-images/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        alt = img.get('alt')
        if src and ('wp-content/uploads' in src or 'images.nasa.gov' in src):
            if not src.startswith('http'):
                src = 'https://science.nasa.gov' + src
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
    image_folder = os.path.join(current_app.static_folder, 'img', 'slideshow')
    all_images = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Xử lý phân trang
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Số lượng hình ảnh mỗi trang
    total_images = len(all_images)
    total_pages = math.ceil(total_images / per_page)
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_images = all_images[start_index:end_index]
    
    return render_template('admin/imageNasa.html', 
                           local_images=paginated_images, 
                           current_page=page, 
                           total_pages=total_pages,
                           per_page=per_page)

def create_unique_filename(alt_text):
    # Xử lý alt text để tạo tên file hợp lệ
    base_name = re.sub(r'[^\w\s-]', '', alt_text)
    base_name = re.sub(r'[-\s]+', '_', base_name).strip('-_').lower()
    
    # Giới hạn độ dài tên file
    base_name = base_name[:100]  # Có thể điều chỉnh độ dài tùy ý
    
    return f"{base_name}.png"

@slideshow_bp.route('/save_images', methods=['POST'])
def save_images():
    data = request.json
    image_data = data.get('images', [])
    image_folder = os.path.join(current_app.static_folder, 'img', 'slideshow')
    
    saved_images = []
    for image in image_data:
        try:
            url = image['src']
            alt_text = image['alt']
            response = requests.get(url)
            if response.status_code == 200:
                filename = create_unique_filename(alt_text)
                filepath = os.path.join(image_folder, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                saved_images.append(filename)
        except Exception as e:
            print(f"Error saving image {url}: {e}")
    
    return jsonify({
        'message': f'Đã lưu {len(saved_images)} hình ảnh thành công',
        'saved_images': saved_images
    })

@slideshow_bp.route('/delete_image', methods=['POST'])
def delete_image():
    data = request.json
    image_name = data.get('image')
    image_folder = os.path.join(current_app.static_folder, 'img', 'slideshow')
    
    if image_name:
        image_path = os.path.join(image_folder, image_name)
        if os.path.exists(image_path):
            os.remove(image_path)
            return jsonify({'message': 'Image deleted successfully'}), 200
        else:
            return jsonify({'error': 'Image not found'}), 404
    else:
        return jsonify({'error': 'No image name provided'}), 400

@slideshow_bp.route('/add_nasa_images', methods=['GET'])
@login_required
def add_nasa_images():
    return render_template('admin/imageNasa_add.html')

@slideshow_bp.route('/get_images')
def get_images():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    image_folder = os.path.join(current_app.static_folder, 'img', 'slideshow')
    all_images = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    # Xáo trộn danh sách hình ảnh
    random.shuffle(all_images)
    
    # Lấy 5 hình ảnh đầu tiên sau khi xáo trộn
    selected_images = all_images[:5]

    total_images = len(all_images)
    total_pages = math.ceil(total_images / per_page)
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_images = all_images[start_index:end_index]
    
    print(f"Returning {len(paginated_images)} images for page {page}")  # Thêm log này
    
    return jsonify({
        'images': selected_images, 
        'total_pages': total_pages,
        'current_page': page
    })