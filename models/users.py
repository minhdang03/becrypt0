from flask_sqlalchemy import SQLAlchemy
from models.config import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Role(db.Model):
    __tablename__ = 'roles'  # Đổi tên bảng thành 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)

    @staticmethod
    def insert_roles():
        roles = {
            'admin': 1,
            'moderator': 2,
            'user': 3
        }
        for role_name, role_id in roles.items():
            role = Role.query.filter_by(role_name=role_name).first()
            if role is None:
                role = Role(role_id=role_id, role_name=role_name)
                db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f'<Role {self.role_name}>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    fullname = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), default=3)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'fullname': self.fullname,
            'role_id': self.role_id,
            'role': self.role.role_name if self.role else None
        }

    def get_id(self):
        return str(self.user_id)

    @property
    def is_authenticated(self):
        return True  # Hoặc logic xác thực phù hợp với ứng dụng của bạn