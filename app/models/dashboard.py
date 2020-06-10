"""
Dashboard Forms
"""

from flask_wtf import FlaskForm

from wtforms import BooleanField
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms import validators


class TargetForm(FlaskForm):
    '''Target Form'''
    id = IntegerField('Target ID', validators=[validators.Optional()])
    domain = StringField('Domain', validators=[
        validators.DataRequired('The domain is required')])
    identifier = StringField('Identifier', validators=[
        validators.DataRequired('A short identifier is required')])
    sleep = IntegerField('Sleep', default=30, validators=[
        validators.DataRequired()])
    providers = SelectMultipleField('Proxy Providers', coerce=int,
                                    validators=[validators.Optional()])
    plans = SelectMultipleField('Provider Plans', coerce=int,
                                validators=[validators.Optional()])


class ProxyTypeForm(FlaskForm):
    '''Proxy Type Form'''
    id = IntegerField('Proxy Type ID', validators=[validators.Optional()])
    name = StringField('Type Name', validators=[
        validators.Length(min=1, max=20),
        validators.DataRequired('A name is required')])
    code = StringField('Type Code', validators=[
        validators.Length(min=1, max=4),
        validators.DataRequired('A code is required')])


class ProxyLocationForm(FlaskForm):
    '''Proxy Location Form'''
    id = IntegerField('Proxy Location ID', validators=[validators.Optional()])
    name = StringField('Location Name', validators=[
        validators.Length(min=1, max=256),
        validators.DataRequired('A name is required')])
    code = StringField('Location Code', validators=[
        validators.Length(min=1, max=4),
        validators.DataRequired('A code is required')])


class ProviderForm(FlaskForm):
    '''Provider Form'''
    id = IntegerField('Provider ID', validators=[validators.Optional()])
    name = StringField('Provider Name', validators=[
        validators.Length(min=1, max=256),
        validators.DataRequired('A name is required')])
    url = StringField('Provider URL', validators=[
        validators.URL(),
        validators.Optional()])
    code = StringField('Provider Code', validators=[
        validators.Length(min=1, max=8),
        validators.DataRequired('A code is required')])


class ProviderPlanForm(FlaskForm):
    '''Provider Plan Form'''
    id = IntegerField('Provider Plan ID', validators=[validators.Optional()])
    provider = SelectField('The Provider', coerce=int, validators=[validators.DataRequired()])
    name = StringField('Provider Plan Name', validators=[
        validators.Length(min=1, max=256),
        validators.DataRequired('A name is required')])
    code = StringField('Provider Plan Code', validators=[
        validators.Length(min=1, max=8),
        validators.DataRequired('A code is required')])


class ProxyForm(FlaskForm):
    '''Proxy Form'''
    id = IntegerField('Proxy ID', validators=[validators.Optional()])
    url = StringField('Proxy URL', validators=[
        validators.URL(),
        validators.DataRequired('URL is required')])
    active = BooleanField('Active', default=True, validators=[validators.DataRequired()])
    proxy_type = SelectField('Proxy Type', coerce=int, validators=[validators.DataRequired()])
    proxy_location = SelectField('Proxy Location ID', coerce=int, validatores=[validators.Optional()])
    provider = SelectField('Provider ID', coerce=int, validators=[validators.Optional()])
    provider_plan = SelectField('Provider Plan ID', coerce=int, validators=[validators.Optional()])
    tor_control_port = IntegerField('Tor Control Port', validators=[validators.Optional()])
    tor_control_pswd = StringField('Tor Control Password', validators=[validators.Optional()])
    tor_renew_identity = BooleanField('Tor Renew Identity',
                                      description='For Tor: force renew identity when blocked',
                                      default=False,
                                      validators=[validators.Optional()])
    dont_block = BooleanField('Do Not Block',
                              description='Never mark proxy as blocked - Do Not Sleep',
                              default=False, validators=[validators.Optional()])
