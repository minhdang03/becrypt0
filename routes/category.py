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

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def category_list():
    categories = Category.query.all()
    form = CategoryForm()
    return render_template('admin/category.html', categories=categories, form=form)

@categories_bp.route('/categories/new', methods=['POST'])
def category_create():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Danh mục đã được thêm thành công!', 'success')
    return redirect(url_for('categories.category_list'))

@categories_bp.route('/categories/edit/<int:category_id>', methods=['POST'])
def category_edit(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Danh mục đã được cập nhật!', 'success')
    return redirect(url_for('categories.category_list'))

@categories_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
def category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Danh mục đã được xóa!', 'success')
    return redirect(url_for('categories.category_list'))