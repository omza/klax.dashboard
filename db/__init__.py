# imports & globals
from datetime import datetime
from sqlalchemy import create_engine
from .models import Base, User, Device, Loadprofile
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import sessionmaker, Session
from config import config, logging


def init_db():

    # Create Database if not exists
    if not database_exists(config.DATABASE_URI):
        create_database(config.DATABASE_URI)

    # Instanciate database engine
    dbengine = create_engine(config.DATABASE_URI, connect_args={'check_same_thread': False})

    # Bind Models to Engine, Create Models in DB if not exists
    Base.metadata.create_all(dbengine)
    # extend_existing=True

    # Instantiate an return Sessionmakerobject
    dbsession = sessionmaker(bind=dbengine)()


    # Create User
    user =  dbsession.query(User).first()
    if not user:
        user = User(firstname=config.USER_FIRSTNAME, email=config.USER_EMAIL)
        user.set_password(config.USER_PASS)
        dbsession.add(user)
        dbsession.commit()
        logging.debug(f"User {user} created")


    # Create Device
    device =  dbsession.query(Device).first()
    if not device:

        device = Device(
            device_extern_id=config.END_DEVICE_ID,
            inserted_at=datetime.now(),
            comment= "",
            dev_eui= "",
            batteryPerc = 99,
            configured= True, 
            connTest= False, 
            deviceType= "SML Klax",
            meterType= "SML",
            version= 1,
            mqtt_topic= "",
            register0_name="1.8.0",
            register0_Active= True,
            register0_unit= "kWh",
            register1_name="2.8.0",
            register1_Active= True,
            register1_unit = "kWh",
            register2_Active = False,     
            register3_Active = False
        ) 

        dbsession.add(device)
        dbsession.commit()
        logging.debug(f"Device {device} created")        


    dbsession.close_all()

    return 

def NewSession(): 

    # Instanciate database engine
    dbengine = create_engine(config.DATABASE_URI, connect_args={'check_same_thread': False})
    # Instantiate an return Sessionmakerobject
    dbsession = sessionmaker(bind=dbengine)()

    return dbsession