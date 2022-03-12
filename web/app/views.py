# imports & globals
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from sqlalchemy import text

from datetime import datetime, timedelta
import time
from werkzeug.exceptions import HTTPException
import json

from app import app, db, logging
from app.forms import LoginForm, RegisterForm, UserDataForm, UserResetPasswordForm, LocationForm, LocationSpeedLimitForm, LocationLocationForm
from app.models import User, Device, HttpStatusCode, Measurement
from app.logic import utc2local_str, utc2local_date_str, random_color_rgba, number_format

# Errorhandling
@app.errorhandler(Exception)
def handle_exception(e):

    try:
        # pass through HTTP errors
        if isinstance(e, HTTPException):
            errorcode = e.code
            errorname = HttpStatusCode(errorcode).name
            errordescription = e.description

        elif isinstance(e, Exception):
            # retrieve error data
            errorcode = 500
            errorname = e.name
            errordescription = e.description
            db.session.rollback()

        else:
            errorcode = 500
            errorname = 'unknown'
            errordescription = 'uups...something went wrong'
    except:
        errorcode = 500
        errorname = 'unknown'
        errordescription = 'uups...something went wrong'

    # logging
    logging.error(f"uups... something went wrong: {errorcode}: {errorname} , {errordescription}")

    # now you're handling errors
    return render_template('error.html', title=errorname, code=errorcode, description=errordescription), e.code

# routes
@app.route('/')
#@app.route('/locations/<device_id>', methods=['GET', 'POST'])
def index(device_id=None):
    """ show the speedfreak metrics charts and tables """


    """
    # Speedfreak data
    device = Devices.query.filter(Devices.active == True).first()

    if device:

        # Speedfreak metrics dictionary
        metrics={}

        # Temperature
        metrics['temp'] = {'name': 'Temperatur', 'unit': '°C', 'value': number_format(device.temp)}
        metrics['so2'] = {'name': 'Schwefeldioxid', 'unit': 'ppm', 'value': number_format(device.so2)}
        metrics['pres'] = {'name': 'Luftdruck', 'unit': 'Pa', 'value': number_format(device.pres)}
        metrics['hum'] = {'name': 'Luftfeuchte', 'unit': '%', 'value': number_format(device.hum)}
        metrics['power'] = {'name': 'Batterieladung', 'unit': '%', 'value': str(int(device.power))}
        metrics['pm25'] = {'name': 'Feinstaub 25µm', 'unit': 'µg/m³', 'value': number_format(device.pm25)}
        metrics['pm10'] = {'name': 'Feinstaub 10µm', 'unit': 'µg/m³', 'value': number_format(device.pm10)}
        metrics['pm1'] = {'name': 'Feinstaub 1µm', 'unit': 'µg/m³', 'value': number_format(device.pm1)}
        metrics['o3'] = {'name': 'Ozon', 'unit': 'ppm', 'value': number_format(device.o3)}
        metrics['no2'] = {'name': 'Stickstoffdioxid', 'unit': 'ppm', 'value': number_format(device.no2)}
        metrics['co'] = {'name': 'Kohlenmonoxid', 'unit': 'ppm', 'value': number_format(device.co)}

        last_tick_at = utc2local_str(device.last_tick_at)
        first_tick_at = utc2local_str(device.first_tick_at)
        metrics['last_tick_at'] = str(last_tick_at)
        metrics['first_tick_at'] = str(first_tick_at)

        # Measurements last 24 Hours (from last_tick_at)
        measurements = None
        if current_user.is_authenticated:

            date_from = device.last_tick_at - timedelta(hours=24)
            sql = "SELECT measured_at, temp, pres, hum, pm25, pm10, pm1, so2, o3, no2, co FROM measurements WHERE device_id = " + str(device.device_id) + \
                " AND measured_at >= '" + date_from.strftime('%Y-%m-%d') + "' ORDER BY measured_at DESC"
            logging.debug(sql)
            result = db.engine.execute(sql)

            measurements = []
            for r in result:

                local_datetime = utc2local_str(r['measured_at'])

                measurements.append({
                    'measured_at': local_datetime,
                    'temp': number_format(r.temp),
                    'pres': number_format(r.pres),
                    'hum': number_format(r.hum),
                    'pm25': number_format(r.pm25),
                    'pm10': number_format(r.pm10),
                    'pm1': number_format(r.pm1),
                    'so2': number_format(r.so2),
                    'o3': number_format(r.o3),
                    'no2': number_format(r.no2),
                    'co': number_format(r.co)
                })

        
        # Speedlimit or Category changes are pending
        if speedfreak.rebuild_until_measurement_id > 0:
            flash('Kategorisierung der Messungen läuft...', 'warning')
        """
    return "klax dashboard" #render_template('locations_show.html', title=device.name, device=device, data=metrics, measurements=measurements, form=LocationForm(), setlocationform=LocationLocationForm())

    """
    else:
        flash('Das Device konnte ich nicht finden!', 'warning')
        redirect(url_for('index'))"""

"""
@app.route('/locations/add/<speedfreak_id>')
def locations_add(speedfreak_id):
   
    if current_user.is_authenticated and current_user.admin:

        # Speedfreak data
        speedfreak = Speedfreak.query.filter(Speedfreak.speedfreak_id == speedfreak_id).first()

        if speedfreak:
            speedfreak.active = True
            db.session.commit()

        speedfreaks = Speedfreak.query.all()

        app.jinja_env.globals['speedfreaks'] = speedfreaks

        return redirect(url_for('locations_show', speedfreak_id=speedfreak_id))

    else:
        flash('Nur Administratoren können Speedfreaks anmelden!', 'warning')
        return redirect(url_for('index'))

@app.route('/locations/disconnect/<speedfreak_id>')
def locations_disconnect(speedfreak_id):

    if current_user.is_authenticated and current_user.admin:

        # Speedfreak data
        speedfreak = Speedfreak.query.filter(Speedfreak.speedfreak_id == speedfreak_id).first()

        if speedfreak:
            speedfreak.active = False
            db.session.commit()

        # speedfreaks = Speedfreak.query.all()

        # app.jinja_env.globals['speedfreaks'] = speedfreaks

        return redirect(url_for('index'))

    else:
        flash('Nur Administratoren können Speedfreaks abmelden!''warning')
        return redirect(url_for('locations_show', speedfreak_id=speedfreak_id))

@app.route('/locations/speedlimit/<speedfreak_id>', methods=['POST'])
@login_required
def locations_setspeedlimit(speedfreak_id):


    form = LocationSpeedLimitForm()

    if form.validate_on_submit():

        # Speedfreak data
        speedfreak = Speedfreak.query.filter(Speedfreak.speedfreak_id == speedfreak_id).first()
        if speedfreak:

            if speedfreak.speedlimit != form.speedlimit.data:

                # set Speedfreak speeding metrics to 0
                speedfreak.speedlimit = form.speedlimit.data
                speedfreak.rebuild_until_measurement_id = 1
                db.session.commit()

                flash('Speedlimit wurde gesetzt!', 'success')

        else:
            flash('Speedfreak wurde nicht gefunden', 'danger')
            return redirect(url_for('index'))

    return redirect(url_for('locations_show', speedfreak_id=speedfreak_id))

@app.route('/devices/edit/<device_id>', methods=['POST'])
@login_required
def device_edit(device_id):


    # Speedfreak data form
    form = LocationForm()

    if form.validate_on_submit():
        logging.debug(f"post device id: {form.name.data}")

        # Speedfreak data
        device = Devices.query.filter(Devices.device_id == device_id).first()
        if device:

            device.name = form.name.data
            device.comment = form.comment.data
            db.session.commit()

            flash(device.name + ' gespeichert', 'success')

        else:
            flash('Device wurde nicht gefunden', 'danger')
            return redirect(url_for('index'))

    return redirect(url_for('index', device_id=device_id))


@app.route('/devices/location/<device_id>', methods=['POST'])
@login_required
def device_setlocation(device_id):

    form = LocationLocationForm()
    print("Location set: " + str(device_id))
    if form.validate_on_submit():
        print("Location set validated")
        # Speedfreak data
        device = Devices.query.filter(Devices.device_id == device_id).first()
        if device:

            # set location
            device.location_longitude = form.location_longitude.data
            device.location_latitude = form.location_latitude.data
            device.location_display_name = form.location_display_name.data
            db.session.commit()

            flash('Standort wurde gesetzt!', 'success')

        else:
            flash('Device wurde nicht gefunden', 'danger')
            return redirect(url_for('index'))

    return redirect(url_for('index', device_id=device_id))


# authentification routes
@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        logging.debug(f"try login user {form.email.data} with email {form.password.data}")

        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        logging.debug(f"try create user {form.email.data} with email {form.password.data}")

        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            # Create new user
            user = User(lastname=form.lastname.data, firstname=form.firstname.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            logging.debug(f"User root {user} created")

        login_user(user, remember=False)
        return redirect(url_for('index'))

    return render_template('register.html', title='Register', form=form)

@app.route('/user/<user_id>', methods=["GET", "POST"])
@login_required
def user(user_id):


    form = UserDataForm()
    form_password = UserResetPasswordForm()

    if form.validate_on_submit():
        # update user
        user = User.query.get(current_user.id)
        user.lastname = form.lastname.data
        user.firstname = form.firstname.data
        user.email = form.email.data
        db.session.commit()

        logging.debug(f"User {user} merged")
        flash('Speichern erfolgreich', 'success')

    return render_template('user.html', title='Profil', form=form, form_password=UserResetPasswordForm())

@app.route('/resetpass/<user_id>', methods=["POST"])
@login_required
def resetpassword(user_id):


    form = UserResetPasswordForm()

    if form.validate_on_submit():
        # Check old password
        user = User.query.get(current_user.id)

        if not user.check_password(form.password_old.data):
            flash('Altes Passwort ist nicht korrekt', 'warning')
        else:
            user.set_password(form.password_new.data)
            db.session.commit()
            flash('Passwort wurde geändert!', 'success')

    return render_template('user.html', title='Profil', form=UserDataForm(), form_password=form)
"""