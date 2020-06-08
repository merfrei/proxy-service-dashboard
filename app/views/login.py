"""
Authentication views

- Login
- Logout
"""

from flask import Blueprint
from flask import render_template
from flask import abort
from flask import redirect
from flask import url_for
from flask import request

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

from app.utils.url import is_safe_url
from app.models.users import User
from app.models.users import LoginForm


login_blueprint = Blueprint('login', __name__, template_folder='login')


@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''Log a User in'''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.login(form)
        if user is not None:
            login_user(user)
            next_url = request.args.get('next', url_for('dashboard.dashboard'))
            if not is_safe_url(next_url):
                return abort(400)
            return redirect(next_url)
    return render_template('login/login.html', form=form)


@login_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    '''Log the current User out'''
    logout_user()
    return redirect(url_for('login.login'))
