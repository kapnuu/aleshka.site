import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from werkzeug.security import generate_password_hash

__author__ = 'kapnuu'

basedir = Path(__file__).resolve().parent

load_dotenv(find_dotenv())


class Config(object):
    CSRF_ENABLED = True
    # SECRET_KEY = 'all-cats-are-beautiful:)'
    SECRET_KEY = os.getenv('SECRET_KEY')

    database_uri = os.environ.get('DATABASE_URL')
    if database_uri is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(basedir / 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = database_uri.replace('postgres://', 'postgresql://')
    print(f'SQLALCHEMY_DATABASE_URI is {SQLALCHEMY_DATABASE_URI}')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    ROOT = os.environ.get('ROOT')
    if ROOT:
        print(f'ROOT is {ROOT}')
        ROOT_PASSWORD = generate_password_hash(os.getenv('ROOT_PASSWORD'))
    else:
        print('ROOT is undefined')
        ROOT_PASSWORD = None

    LANGUAGES = ['en', 'ru']

    LOGIN_TIMEOUT = 20 * 60  # 20 minutes
