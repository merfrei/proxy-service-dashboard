"""
User SQLAlchemy models and Forms
"""

from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import SubmitField
from wtforms import validators

from passlib.apps import custom_app_context as pwd_context

from app import db
from app import login_manager


class User(db.Model):
    '''SQLAlchemy model for users'''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.Unicode(255), unique=True)

    def verify_password(self, pswd):
        '''Verify if the password `pwd` is valid'''
        return pwd_context.verify(pswd, self.password)

    def set_password(self, pswd):
        '''Set a new password for the current user'''
        self.password = pwd_context.encrypt(pswd)

    @classmethod
    def login(cls, form):
        '''From a WTF form it will validate the username/password
        Return the User if valid'''
        user = cls.query.filter(cls.username == form.username.data).first()
        if user is not None:
            if user.verify_password(form.password.data):
                return user
        return None

    def is_authenticated(self):
        '''Flask-Login is_authenticated method'''
        return True

    def is_active(self):
        '''Flask-Login is_active method'''
        return True

    def is_anonymous(self):
        '''Flask-Login is_anonymous method'''
        return False

    def get_id(self):
        '''Flask-Login get_id method'''
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class LoginForm(FlaskForm):
    '''The Login Form'''
    username = StringField('Username', validators=[
        validators.DataRequired('The username is required')])
    password = StringField('Password', validators=[
        validators.DataRequired('Your password is required')])
    submit = SubmitField('Save')


@login_manager.user_loader
def load_user(user_id):
    '''The load_user method for flask_login'''
    return User.query.get(user_id)
