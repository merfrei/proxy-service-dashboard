"""
Views - Register blueprints
"""

from app.views.login import login_blueprint
from app.views.dashboard import dashboard_blueprint


def register_blueprints(app):
    '''Register the blueprints'''
    app.register_blueprint(login_blueprint)
    app.register_blueprint(dashboard_blueprint)
