from models.config import db

class SlideshowImage(db.Model):
    __tablename__ = 'slideshowimage'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255), nullable=True)

    def __init__(self, url, alt_text):
        self.url = url
        self.alt_text = alt_text
