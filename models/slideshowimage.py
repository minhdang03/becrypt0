from models.config import db

class SlideshowImage(db.Model):
    __tablename__ = 'slideshowimage'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255), nullable=True)
    is_firstimageblogs = db.Column(db.Boolean, nullable=False, default=False)  # Thêm cột is_firstimageblogs

    def __init__(self, url, alt_text, is_firstimageblogs=False):
        self.url = url
        self.alt_text = alt_text
        self.is_firstimageblogs = is_firstimageblogs