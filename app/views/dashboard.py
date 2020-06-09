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
from flask import url_for
from flask import redirect

from flask_login import login_required

from app import psdash
from app.contrib.api import API

from app.models.dashboard import TargetForm


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


def get_api_options(endpoint, id_field='id', val_field='name'):
    '''Call the API en return a list of tuples [(<id>, <value>), ...]'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    resp = api.get(endpoint)
    return [(res[id_field], res[val_field]) for res in resp['data']]


def update_api_relations(endpoint, parent_field, child_field, parent_id, *child_ids):
    '''Update the relations so the parent_id will be related to the all the child_ids
    All the existing data will be wiped and replaced with this new one'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    params = {parent_field: parent_id}
    resp = api.get(endpoint, **params)
    for data in resp['data']:
        api.delete(endpoint, data['id'])
    for child_id in child_ids:
        new_rel = params.copy()
        new_rel[child_field] = child_id
        api.post(endpoint, **new_rel)

def generate_related_ids(endpoint, parent_field, child_field, parent_id):
    '''Given an endpoint (relation) and a parent ID it will generate all the child IDs'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    params = {parent_field: parent_id}
    resp = api.get(endpoint, **params)
    for data in resp['data']:
        yield data[child_field]


def add_update_target_data(form):
    '''Given a TargetForm it will call the API and add the data'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    target_id = form.id.data
    target_data = {
        'domain': form.domain.data,
        'identifier': form.identifier.data,
        'blocked_standby': form.sleep.data,
    }
    if target_id:
        # It is an update
        api.put('target', target_id, **target_data)
    else:
        # Create the new target
        resp = api.post('target', **target_data)
        target_id = resp['data']['id']
    # Update Target/Provider relations
    if form.providers.data:
        update_api_relations(
            'target_provider', 'target_id', 'provider_id', **form.providers.data)
    # Update Target/Plan relations
    if form.plans.data:
        update_api_relations(
            'target_provider_plan', 'target_id', 'provider_plan_id', **form.plans.data)

def delete_target(target_id):
    '''Delete the Target'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    api.delete('target', target_id)


def populate_target_form(form, target_id):
    '''Given a target ID it will populate the form with the data returned form the API'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    target = api.get('target', elem_id=target_id)['data']
    if target:
        form.id.data = target_id
        form.domain.data = target['domain']
        form.identifier.data = target['identifier']
        form.sleep.data = target['blocked_standby']
        form.providers.data = generate_related_ids(
            'target_provider', 'target_id', 'provider_id', target_id)
        form.plans.data = generate_related_ids(
            'target_provider_plan', 'target_id', 'provider_plan_id', target_id)


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


@dashboard_blueprint.route('/target/edit', methods=['GET', 'POST'])
@login_required
def target_edit():
    '''Add a new target or edit an existing one'''
    form = TargetForm()
    if form.validate_on_submit():
        target_delete_flag = request.args.get('delete')
        if target_delete_flag:
            delete_target(form.id.data)
        else:
            add_update_target_data(form)
        return redirect(url_for('dashboard.targets'))
    target_id = abs(request.args.get('id', 0, type=int))
    if target_id:
        populate_target_form(form, target_id)
    form.providers.choices = get_api_options('provider')
    form.plans.choices = get_api_options('provider_plan')
    return render_template('dashboard/target_edit.html', form=form)


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
