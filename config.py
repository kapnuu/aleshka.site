import os
from werkzeug.security import generate_password_hash

__author__ = 'kapnuu'

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = 'all-cats-are-beautiful:)'
    # SECRET_KEY = os.urandom(16)

    database_uri = os.environ.get('DATABASE_URL')
    if database_uri is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = database_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    ROOT = os.environ.get('ROOT')
    if ROOT:
        ROOT_PASSWORD = generate_password_hash(os.getenv('ROOT_PASSWORD'))
    else:
        ROOT_PASSWORD = None
