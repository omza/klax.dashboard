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

logging.info(f"klax simple dashboard  Startup....")
logging.debug(f"configuration: {app.config}")

""" Database Configuration """
# Create demo device if there are no one
if config.DEMO_MODE:

    # Create Database if not exists
    if not database_exists(config.MYSQL_DATABASE_URI):
        create_database(config.MYSQL_DATABASE_URI)

    db = SQLAlchemy(app)
    from app.models import User, Device, Measurement

    db.create_all()

    # Create Superuser
    user = User.query.first()
    if not user:
        user = User(firstname='admin', email='admin@ao-t.de')
        user.set_password(config.MYSQL_ROOT_PASSWORD)
        db.session.add(user)
        db.session.commit()
        logging.debug(f"User root {user} created")    


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
#from app import datastreams
