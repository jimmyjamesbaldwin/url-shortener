import os
import sys
import urllib.parse

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    APP_NAME = os.environ.get('APP_NAME')
    SECRET_KEY = os.environ.get('APP_NAME') or os.urandom(24)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://' + os.environ.get('DATABASE_USERNAME') + \
        ':' + os.environ.get('DATABASE_PASSWORD') + \
        '@' + os.environ.get('DATABASE_HOST') + \
        '/' + os.environ.get('DATABASE_DB')

    @classmethod
    def init_app(cls, app):
        app.logger.debug('*** Running in Debug mode ***')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        app.logger.debug('*** Running in Test mode ***')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://' + os.environ.get('DATABASE_USERNAME') + \
        ':' + os.environ.get('DATABASE_PASSWORD') + \
        '@' + os.environ.get('DATABASE_HOST') + \
        '/' + os.environ.get('DATABASE_DB')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.logger.debug('*** Running in Production baby! ***')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
