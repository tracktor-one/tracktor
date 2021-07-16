import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', default='you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             default='sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USER = os.environ.get('ADMIN_USER', default='admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', default='password')
