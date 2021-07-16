import enum
import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash

from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_login = db.Column(db.DateTime, default=None)
    admin = db.Column(db.Boolean(), default=False)

    def toJSON(self):
        return {
            "id": self.public_id, "name": self.name,
            "created_at": self.created_at, "last_login": self.last_login,
            "admin": self.admin
        }

    def is_username_valid(self, username: str):
        check_user = User.query.filter_by(name=username).first()
        return not check_user or self.id == check_user.id

    def update_password(self, password: str) -> bool:
        if not password:
            return False
        self.password = generate_password_hash(password)
        db.session.commit()
        return True

    @staticmethod
    def create(name: str, password="", admin=False):
        user_uuid = str(uuid.uuid1())
        user = User(
            name=name,
            public_id=user_uuid,
            password=generate_password_hash(password) if password else None,
            admin=admin
        )
        db.session.add(user)
        db.session.commit()
        return user
