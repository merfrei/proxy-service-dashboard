"""
Authentication views

- Login
- Logout
"""

from flask import Blueprint
from flask import render_template

from app.models.users import LoginForm


auth_blueprint = Blueprint('auth', __name__, template_folder='auth')
