from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Optional

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Fullname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password', message='Passwords must match')])
    role_id = SelectField('Role', choices=[(1, 'Admin'), (2, 'User')], coerce=int)
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    fullname = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')