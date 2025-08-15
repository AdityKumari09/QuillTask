from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db   

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    todos = db.relationship('Todo', backref='user', lazy=True)

    def set_password(self, password):
        """Hash karke password store karega."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Login time password verify karega."""
        return check_password_hash(self.password_hash, password)
