from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange

# User Forms
class LoginForm(FlaskForm):
    email = StringField('eMail Adresse', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    firstname = StringField('Vorname', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('passwordrepeat', message='Passwords must match')])
    passwordrepeat = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    submit = SubmitField('Register')

class UserDataForm(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    firstname = StringField('Vorname', validators=[DataRequired()])

class UserResetPasswordForm(FlaskForm):
    password_old = PasswordField('Altes Passwort', validators=[DataRequired()])
    password_new = PasswordField('Neues Passwort', validators=[DataRequired(), EqualTo('passwordrepeat', message='Passwords must match')])
    passwordrepeat = PasswordField('Passwort wiederholen', validators=[DataRequired()])

# Speedfreak Forms
class LocationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    comment = StringField('Kommentar', validators=[DataRequired()])
    """
    speed_alarm_threshold = IntegerField('Schwelle Alarm km/h', validators=[DataRequired()])
    speed_alarm_label = StringField('Bezeichnung Alarm', validators=[DataRequired()])
    speed_warning_threshold = IntegerField('Schwelle Warnung km/h', validators=[DataRequired()])
    speed_warning_label = StringField('Bezeichnung Warnung', validators=[DataRequired()])"""

class LocationSpeedLimitForm(FlaskForm):
    speedlimit = IntegerField('Limit km/h', validators=[NumberRange(min=1, max=60)])

class LocationLocationForm(FlaskForm):
    location_longitude = FloatField('Longitude', validators=[DataRequired()])
    location_latitude = FloatField('Latitude', validators=[DataRequired()])
    location_display_name = StringField('Standort', validators=[DataRequired()])
