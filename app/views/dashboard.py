"""
Dashboard views

- Targets
- Proxies
- Types
- Locations
- Providers
- Stats

"""

from flask import Blueprint
from flask import render_template

from flask_login import login_required


dashboard_blueprint = Blueprint('dashboard', __name__, template_folder='dashboard')


@dashboard_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    '''The main Dashboard'''
    return render_template('dashboard/dashboard.html')
