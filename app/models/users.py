"""
User SQLAlchemy models and Forms
"""

from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import SubmitField
from wtforms import validators

from app import db


class User(db.Model):
    '''SQLAlchemy model for users'''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.Unicode(255), unique=True)


class LoginForm(FlaskForm):
    '''The Login Form'''
    username = StringField('Username', validators=[
        validators.DataRequired('The username is required')])
    password = StringField('Password', validators=[
        validators.DataRequired('Your password is required')])
    submit = SubmitField('Save')
