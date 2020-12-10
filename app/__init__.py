import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)

    if not os.environ.get('HEROKU'):
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/aleshka.log', 'a', 1 * 1024 * 1024, 10)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Aleshka.site startup @ localhost')
    else:
        stream_handler = logging.StreamHandler()
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.info('Aleshka.site startup @ heroku')

        # TODO add notifiers to log

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


from app import models
