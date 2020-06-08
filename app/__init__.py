"""
Flask - Proxy Service Dashboard App
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from app.config import get_config

config = get_config()

psdash = Flask(__name__)
psdash.config['APP_DOMAINS'] = {domain for domain in config['app']['domains']}
psdash.config['SECRET_KEY'] = config['app']['secret_key']
psdash.config['SQLALCHEMY_DATABASE_URI'] = config['database']['uri']
psdash.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
psdash.config['api_key'] = config['api']['api_key']

# Setup Flask-SQLAlchemy
db = SQLAlchemy(psdash)

# Setup WTForms CSRFProtect
csrf_protect = CSRFProtect(psdash)

# Login Manager
login_manager = LoginManager(psdash)
login_manager.login_view = 'login.login'
