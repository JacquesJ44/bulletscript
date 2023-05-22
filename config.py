# Flask configuration

import os 
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # Base config
    SECRET_KEY = os.urandom(12).hex()
    # Session config
    # SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    # Folder and template config
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    TEMPLATES_AUTO_RELOAD = True
    # Config for mail server
    MAIL_SERVER = os.environ.get('EMAIL_HOST')
    MAIL_PORT = os.environ.get('EMAIL_PORT')
    MAIL_USERNAME = os.environ.get('EMAIL_HOST_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    MAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL')
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Testing - mails will not send if set to true
    TESTING = False
    DEBUG = True
