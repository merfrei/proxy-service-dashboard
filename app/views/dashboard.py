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
from app.models.dashboard import ProxyForm
from app.models.dashboard import ProxyTypeForm
from app.models.dashboard import ProxyLocationForm
from app.models.dashboard import ProviderForm
from app.models.dashboard import ProviderPlanForm


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


def add_update_data(endpoint, form, *fields_map):
    '''Basic update API from Form function
    @param endpoint: API endpoint
    @param form: a FlaskForm instance
    @fields_map: a list of tuples [(<api_field>, <form_field>), ...]'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    elem_id = form.id.data
    data = {f_map[0]: getattr(form, f_map[1]).data for f_map in fields_map}
    if elem_id:
        # It is an update
        api.put(endpoint, elem_id, **data)
    else:
        # Create the new element
        api.post(endpoint, **data)


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
            'target_provider', 'target_id', 'provider_id', target_id, *form.providers.data)
    # Update Target/Plan relations
    if form.plans.data:
        update_api_relations(
            'target_provider_plan', 'target_id', 'provider_plan_id', target_id, *form.plans.data)


def add_update_proxy_data(form):
    '''Given a ProxyForm it will call the API and add the data'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    proxy_id = form.id.data
    proxy_data = {
        'url': form.url.data,
        'active': form.active.data,
        'proxy_type_id': form.proxy_type.data,
        'proxy_location_id': form.proxy_location.data,
        'provider_id': form.provider.data,
        'provider_plan_id': form.provider_plan.data,
        'tor_control_port': form.tor_control_port.data,
        'tor_control_pswd': form.tor_control_pswd.data,
        'tor_renew_identity': form.tor_renew_identity.data,
        'dont_block': form.dont_block.data,
    }
    if proxy_id:
        # It is an update
        api.put('proxy', proxy_id, **proxy_data)
    else:
        # Create the new proxy
        api.post('proxy', **proxy_data)


def delete_element(endpoint, elem_id):
    '''Delete an element from the API'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    api.delete(endpoint, elem_id)


def populate_form(endpoint, form, elem_id, *fields_map):
    '''Basic funtion to populate form instance with data from the API
    Similar to add_update_data but on the contrary. See that function for more details'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    element = api.get(endpoint, elem_id=elem_id)['data']
    if element:
        form.id.data = elem_id
        for api_field, form_field in fields_map:
            getattr(form, form_field).data = element[api_field]


def populate_target_form(form, target_id):
    '''Given a target ID it will populate the form with the data returned from the API'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    target = api.get('target', elem_id=target_id)['data']
    if target:
        form.id.data = target_id
        form.domain.data = target['domain']
        form.identifier.data = target['identifier']
        form.sleep.data = target['blocked_standby']
        form.providers.data = set(generate_related_ids(
            'target_provider', 'target_id', 'provider_id', target_id))
        form.plans.data = set(generate_related_ids(
            'target_provider_plan', 'target_id', 'provider_plan_id', target_id))


def populate_proxy_form(form, proxy_id):
    '''Given a proxy ID it will populate the form with the data returned from the API'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    proxy = api.get('proxy', elem_id=proxy_id)['data']
    if proxy:
        form.id.data = proxy_id
        form.url.data = proxy['url']
        form.active.data = proxy['active']
        form.proxy_type.data = proxy['proxy_type_id']
        form.proxy_location.data = proxy['proxy_location_id']
        form.provider.data = proxy['provider_id']
        form.provider_plan.data = proxy['provider_plan_id']
        form.tor_control_port.data = proxy['tor_control_port']
        form.tor_control_pswd.data = proxy['tor_control_pswd']
        form.tor_renew_identity.data = proxy['tor_renew_identity']
        form.dont_block.data = proxy['dont_block']


def return_paginated_list(api_endpoint):
    '''Paginate the results of the API'''
    page, offset, limit = get_current_page_offset_limit()
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    api_resp = api.get(api_endpoint, offset=offset, limit=limit)
    total = api_resp['total']
    results = api_resp['data']
    prev_page, next_page = get_prev_next_page(total, page)
    return results, total, prev_page, next_page


def add_name_to_results(results, id_field, api_endpoint, src_field, name_field):
    '''Add the name for an ID relation field to the results
    For example:

    results = [{'row_id': 1}, {'row_id': 2}]

    add_name_to_results(results, 'row_id', 'rows', 'name', 'row_name')

    results = [{'row_id': 1, 'row_name': 'Row 1'}, {'row_id': 2, 'row_name': 'Row 2'}]

    @param results: the list of results
    @id_field: the key of the object in the results that is the ID for the relation
    @api_endpoint: the endpoint to call for asking the related object
    @src_field: the field I want to add its value to the result object
    @name_field: the name of the new field to be added to the result'''
    api = API(psdash.config['api_url'], psdash.config['api_key'])
    for result in results:
        src_id = result[id_field]
        resp = api.get(api_endpoint, elem_id=src_id)
        result[name_field] = resp['data'][src_field]


@dashboard_blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    '''The main Dashboard'''
    return render_template('dashboard/dashboard.html')


@dashboard_blueprint.route('/targets', methods=['GET'])
@login_required
def targets():
    '''The Targets page'''
    results, total, prev_page, next_page = return_paginated_list('target')
    return render_template('dashboard/targets.html',
                           results=results, total=total,
                           prev_page=prev_page, next_page=next_page)



@dashboard_blueprint.route('/target/edit', methods=['GET', 'POST'])
@login_required
def target_edit():
    '''Add/Edit/Remove a target'''
    form = TargetForm()
    form.providers.choices = get_api_options('provider')
    form.plans.choices = get_api_options('provider_plan')
    if form.validate_on_submit():
        delete_flag = request.args.get('delete')
        if delete_flag:
            delete_element('target', form.id.data)
        else:
            add_update_target_data(form)
        return redirect(url_for('dashboard.targets'))
    elem_id = abs(request.args.get('id', 0, type=int))
    if elem_id:
        populate_target_form(form, elem_id)
    return render_template('dashboard/target_edit.html', form=form)


@dashboard_blueprint.route('/proxies', methods=['GET'])
@login_required
def proxies():
    '''The Proxies page'''
    results, total, prev_page, next_page = return_paginated_list('proxy')
    add_name_to_results(results, 'proxy_type_id', 'proxy_type', 'name', 'type')
    add_name_to_results(results, 'proxy_location_id', 'proxy_location', 'name', 'location')
    add_name_to_results(results, 'provider_id', 'provider', 'name', 'provider')
    add_name_to_results(results, 'provider_plan_id', 'provider_plan', 'name', 'plan')
    return render_template('dashboard/proxies.html',
                           results=results, total=total,
                           prev_page=prev_page, next_page=next_page)


@dashboard_blueprint.route('/proxy/edit', methods=['GET', 'POST'])
@login_required
def proxy_edit():
    '''Add/Edit/Remove a proxy'''
    form = ProxyForm()
    form.proxy_type.choices = get_api_options('proxy_type')
    form.proxy_location.choices = get_api_options('proxy_location')
    form.provider.choices = get_api_options('provider')
    form.provider_plan.choices = get_api_options('provider_plan')
    if form.validate_on_submit():
        delete_flag = request.args.get('delete')
        if delete_flag:
            delete_element('proxy', form.id.data)
        else:
            add_update_proxy_data(form)
        return redirect(url_for('dashboard.proxies'))
    elem_id = abs(request.args.get('id', 0, type=int))
    if elem_id:
        populate_proxy_form(form, elem_id)
    return render_template('dashboard/proxy_edit.html', form=form)


@dashboard_blueprint.route('/types', methods=['GET'])
@login_required
def types():
    '''The Proxy Types page'''
    results, total, prev_page, next_page = return_paginated_list('proxy_type')
    return render_template('dashboard/types.html',
                           results=results, total=total,
                           prev_page=prev_page, next_page=next_page)


@dashboard_blueprint.route('/type/edit', methods=['GET', 'POST'])
@login_required
def type_edit():
    '''Add/Edit/Remove a proxy type'''
    form = ProxyTypeForm()
    if form.validate_on_submit():
        delete_flag = request.args.get('delete')
        if delete_flag:
            delete_element('proxy_type', form.id.data)
        else:
            add_update_data('proxy_type', form, *[('name', 'name'), ('code', 'code')])
        return redirect(url_for('dashboard.types'))
    elem_id = abs(request.args.get('id', 0, type=int))
    if elem_id:
        populate_form('proxy_type', form, elem_id, *[('name', 'name'), ('code', 'code')])
    return render_template('dashboard/type_edit.html', form=form)


@dashboard_blueprint.route('/locations', methods=['GET'])
@login_required
def locations():
    '''The Locations page'''
    results, total, prev_page, next_page = return_paginated_list('proxy_location')
    return render_template('dashboard/locations.html',
                           results=results, total=total,
                           prev_page=prev_page, next_page=next_page)


@dashboard_blueprint.route('/location/edit', methods=['GET', 'POST'])
@login_required
def location_edit():
    '''Add/Edit/Remove a proxy location'''
    form = ProxyLocationForm()
    if form.validate_on_submit():
        delete_flag = request.args.get('delete')
        if delete_flag:
            delete_element('proxy_location', form.id.data)
        else:
            add_update_data('proxy_location', form, *[('name', 'name'), ('code', 'code')])
        return redirect(url_for('dashboard.locations'))
    elem_id = abs(request.args.get('id', 0, type=int))
    if elem_id:
        populate_form('proxy_location', form, elem_id, *[('name', 'name'), ('code', 'code')])
    return render_template('dashboard/location_edit.html', form=form)


@dashboard_blueprint.route('/providers', methods=['GET'])
@login_required
def providers():
    '''The Providers page'''
    results, total, prev_page, next_page = return_paginated_list('provider')
    return render_template('dashboard/providers.html',
                           results=results, total=total,
                           prev_page=prev_page, next_page=next_page)


@dashboard_blueprint.route('/provider/edit', methods=['GET', 'POST'])
@login_required
def provider_edit():
    '''Add/Edit/Remove a proxy provider'''
    form = ProviderForm()
    if form.validate_on_submit():
        delete_flag = request.args.get('delete')
        if delete_flag:
            delete_element('provider', form.id.data)
        else:
            add_update_data('provider', form,
                            *[('name', 'name'), ('url', 'url'), ('code', 'code')])
        return redirect(url_for('dashboard.providers'))
    elem_id = abs(request.args.get('id', 0, type=int))
    if elem_id:
        populate_form('provider', form, elem_id,
                      *[('name', 'name'), ('url', 'url'), ('code', 'code')])
    return render_template('dashboard/provider_edit.html', form=form)


@dashboard_blueprint.route('/plans', methods=['GET'])
@login_required
def plans():
    '''The Providers page'''
    results, total, prev_page, next_page = return_paginated_list('provider_plan')
    add_name_to_results(results, 'provider_id', 'provider', 'name', 'provider')
    return render_template('dashboard/plans.html',
                           results=results, total=total,
                           prev_page=prev_page, next_page=next_page)


@dashboard_blueprint.route('/plan/edit', methods=['GET', 'POST'])
@login_required
def plan_edit():
    '''Add/Edit/Remove a proxy provider plan'''
    form = ProviderPlanForm()
    form.provider.choices = get_api_options('provider')
    if form.validate_on_submit():
        delete_flag = request.args.get('delete')
        if delete_flag:
            delete_element('provider_plan', form.id.data)
        else:
            add_update_data('provider_plan', form,
                            *[('provider_id', 'provider'), ('name', 'name'), ('code', 'code')])
        return redirect(url_for('dashboard.plans'))
    elem_id = abs(request.args.get('id', 0, type=int))
    if elem_id:
        populate_form('provider_plan', form, elem_id,
                      *[('provider_id', 'provider'), ('name', 'name'), ('code', 'code')])
    return render_template('dashboard/plan_edit.html', form=form)


@dashboard_blueprint.route('/stats', methods=['GET'])
@login_required
def stats():
    '''The Targets page'''
    return render_template('dashboard/stats.html')
