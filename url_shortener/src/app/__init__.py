import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask
import peewee as pw
from config import config
import sqlite3
import time
import sys
from pymemcache.client import base

basedir = os.path.abspath(os.path.dirname(__file__))

# Connect to database and memcached
try:
    db = pw.MySQLDatabase("urls", host="db", port=3306, user="root", passwd="root")
    db.connect()
    memcached_client = base.Client(('memcached', 11211))
except Exception as e:
    print('Error connecting to database or memcached: ' + str(e))

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    config[config_name].init_app(app)

    # Set up logger
    handler = RotatingFileHandler(datetime.now().strftime('%Y-%m-%d') + '.log', maxBytes=10000, backupCount=1)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    return app

