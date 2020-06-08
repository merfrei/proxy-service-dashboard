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
from flask import request

from flask_login import login_required

from app import psdash
from app.contrib.api import API


dashboard_blueprint = Blueprint('dashboard', __name__, template_folder='dashboard')


def get_current_page_offset_limit():
    '''Given the current page and page size config it will return the offset/limit to use
    in the API request'''
    page = abs(request.args.get('page', 1, type=int))
    offset = (page - 1) * psdash.config['PAGE_SIZE']
    limit = psdash.config['PAGE_SIZE']
    return page, offset, limit


def get_prev_next_page(total, current_page):
    '''Given the total of items and the current page value
    it will return the previous page and the next page'''
    page_size = psdash.config['PAGE_SIZE']
    next_page = None if (current_page * page_size) > total else current_page + 1
    prev_page = current_page -1 if current_page > 1 else None
    return prev_page, next_page


@dashboard_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    '''The main Dashboard'''
    return render_template('dashboard/dashboard.html')


@dashboard_blueprint.route('/targets', methods=['GET'])
@login_required
def targets():
    '''The Targets page'''
    page, offset, limit = get_current_page_offset_limit()
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    api_resp = api.get('target', offset=offset, limit=limit)
    total = api_resp['total']
    results = api_resp['data']
    prev_page, next_page = get_prev_next_page(total, page)
    return render_template('dashboard/targets.html',
                           targets=results, total=total,
                           prev_page=prev_page, next_page=next_page)


@dashboard_blueprint.route('/proxies', methods=['GET'])
@login_required
def proxies():
    '''The Proxies page'''
    return render_template('dashboard/proxies.html')


@dashboard_blueprint.route('/types', methods=['GET'])
@login_required
def types():
    '''The Proxy Types page'''
    return render_template('dashboard/types.html')


@dashboard_blueprint.route('/locations', methods=['GET'])
@login_required
def locations():
    '''The Locations page'''
    return render_template('dashboard/locations.html')


@dashboard_blueprint.route('/providers', methods=['GET'])
@login_required
def providers():
    '''The Providers page'''
    return render_template('dashboard/providers.html')


@dashboard_blueprint.route('/stats', methods=['GET'])
@login_required
def stats():
    '''The Targets page'''
    return render_template('dashboard/stats.html')
