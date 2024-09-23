from models.config import db

class BlogImage(db.Model):
    __tablename__ = 'blog_images'
    
    image_id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.blog_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    blog = db.relationship('Blog', back_populates='images')