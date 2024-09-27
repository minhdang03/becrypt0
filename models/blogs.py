from flask_sqlalchemy import SQLAlchemy
from models.config import db

class Blog(db.Model):
    __tablename__ = 'blogs'
    blog_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    is_favorite = db.Column(db.Boolean, default=False)
    thumbnail_url = db.Column(db.String(255))  # Add this line

    user = db.relationship('User', backref='blogs')
    images = db.relationship('BlogImage', back_populates='blog', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'blog_id': self.blog_id,
            'user_id': self.user_id,
            'author': self.user.fullname if self.user else None,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'category': self.category.name if self.category else None,
            'is_published': self.is_published,
            'is_favorite': self.is_favorite,
            'thumbnail_url': self.thumbnail_url,  # Add this line
            'images': [image.image_url for image in self.images]
        }