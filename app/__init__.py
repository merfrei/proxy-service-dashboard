"""
Flask - Proxy Service Dashboard App
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from app.config import get_config


# Instantiate Flask extensions
db = SQLAlchemy()
csrf_protect = CSRFProtect()
login_manager = LoginManager()



def create_app():
    '''Create a Flask application'''
    config = get_config()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = config['app']['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = config['database']['uri']
    app.config['api_key'] = config['api']['api_key']

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup WTForms CSRFProtect
    csrf_protect.init_app(app)

    # Login Manager
    login_manager.init_app(app)
