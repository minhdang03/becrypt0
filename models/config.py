from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

DATABASE_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}

def init_app(app):
    app.config.update(DATABASE_CONFIG)
    db.init_app(app)
    with app.app_context():
        db.create_all()