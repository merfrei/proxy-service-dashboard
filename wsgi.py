"""
To use with Gunicorn
"""

from app import psdash as application
from app.views import register_blueprints

register_blueprints(application)
