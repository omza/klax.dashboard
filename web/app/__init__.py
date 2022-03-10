from flask import Flask, request, flash
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import create_database, database_exists
import datetime

""" Flask App Init """
app = Flask(__name__)

""" Configuration object """
from app.configuration import AppConfiguration
config = AppConfiguration()
app.config.from_object(config)


""" Logging Configuration """
import logging
logging.basicConfig(
    filename=config.LOG_FILE,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=config.LOG_LEVEL)

logging.info(f"Alpha Omega Technology (AOT) Sensor Demo App Startup....")
logging.debug(f"configuration: {app.config}")

""" Database Configuration """
# Create Database if not exists
if not database_exists(config.MYSQL_DATABASE_URI):
    create_database(config.MYSQL_DATABASE_URI)

db = SQLAlchemy(app)
from app.models import User, Devices, Connector
db.create_all()

# Create Superuser
user = User.query.filter_by(admin=True).first()
if not user:
    user = User(lastname='ao-t.de', firstname='admin', email='admin@ao-t.de', admin=True)
    user.set_password(config.MYSQL_ROOT_PASSWORD)
    db.session.add(user)
    db.session.commit()
    logging.debug(f"User root {user} created")

# Create DemoSpeedfreak if there are no one
if config.DEMO_MODE:

    connectors = Connector.query.first()

    if not connectors:

        connector = Connector(
            connector_id=1,
            connector_type=1,
            connector_database='elementiotconnector'
        )

        db.session.add(connector)
        db.session.commit()

        devices = Devices.query.all()

        if not devices:

            device = Devices(
                connector_id=1,
                device_extern_id='1',
                name='Smart Environment Demo',
                inserted_at=datetime.datetime.utcnow(),
                location_longitude=0, location_latitude=0,
                active=True,
                online_ticks_per_hour=0,
                online_ticks=0,
                first_tick_at=datetime.datetime.utcnow(),
                last_tick_at=datetime.datetime.utcnow(),
                temp=9.0,
                so2=10.0,
                pres=11.0,
                power=12.0,
                pm25=25.0,
                pm10=10.0,
                pm1=1.0,
                o3=1231.0,
                no2=324234.0,
                hum=35.0,
                co=979.0
            )


            db.session.add(device)
            db.session.commit()



""" flask-login """
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# callback to reload the user object
@login_manager.user_loader
def load_user(userid):

    if userid:
        try:
            user = User.query.get(int(userid))
        except:
            user = None
            flash('Ihre Benutzersession ist abgelaufen. Bitte melden Sie sich erneut an.', 'warning')
        finally:
            return user
    else:
        return None


""" Retrieve Speedfreaks """
# devices = Speedfreak.query.all()

""" Jinja 2 incections """
# app.jinja_env.globals['speedfreaks'] = speedfreaks

@app.context_processor
def inject_template_scope():
    injections = dict()

    def cookies_check():
        value = request.cookies.get('cookie_consent')
        return value == 'true'
    injections.update(cookies_check=cookies_check)

    return injections


""" register views to app instance """
from app import views
from app import datastreams
