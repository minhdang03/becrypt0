from flask_sqlalchemy import SQLAlchemy
from models.config import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    blogs = db.relationship('Blog', backref='category', lazy=True)