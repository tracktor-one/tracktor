from datetime import datetime
from functools import wraps

from flask import Flask
from flask_jwt import JWT, current_identity
from flask_jwt import jwt_required
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def authenticated(admin=False):
    def decorated_function(f):
        @jwt_required()
        @wraps(f)
        def decorated_inner_function(*args, **kwargs):
            if current_identity.admin != admin:
                return jsonify(error='Insufficient permission'), 403
            return f(*args, **kwargs)

        return decorated_inner_function

    return decorated_function


from app.models import *
from app.api import *


def authenticate(username, password):
    potential_user = User.query.filter_by(name=username).scalar()
    if potential_user and check_password_hash(potential_user.password, password):
        potential_user.last_login = datetime.utcnow()
        db.session.commit()
        return potential_user


def identity(payload):
    return User.query.filter_by(id=payload['identity']).scalar()


jwt = JWT(app, authentication_handler=authenticate, identity_handler=identity)


@app.before_first_request
def initialize_first_user():
    if not User.query.all():
        db.session.add(User.create(
            name=Config.ADMIN_USER,
            password=Config.ADMIN_PASSWORD,
            admin=True
        ))
        db.session.commit()
