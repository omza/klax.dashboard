from fastapi import APIRouter

# Login
from fastapi_login import LoginManager
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from config import config, logging

from sqlalchemy import func
from db import  NewSession
from db.models import User, Device, Measurement
from tools.convert import utc2local, local2utc

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

# Login
manager = LoginManager(config.SECRET, 
                        '/api/login',
                        use_cookie=True,
                        cookie_name='myklax_token')

@manager.user_loader()
def query_user(user_id:str = ""):
    
    # retrieve user information
    dbsession = NewSession()
    user =  dbsession.query(User).first() 

    return user

@router.post('/login')
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = query_user()
    if not user:
        # you can return any response or error of your choice
        raise InvalidCredentialsException
    
    elif not user.check_password(password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
    data={'sub': email}
    )

    #manager.set_cookie(data, token)

    return {'access_token': access_token}

@router.get("/device")
async def read_device(user=Depends(manager)):

    # retrieve user information
    dbsession = NewSession()

    #retrieve device data
    device =  dbsession.query(Device).first()

    return device

@router.get("/measurements")
async def read_measurements(user=Depends(manager), register_id: int = -1, date_from: date = date.today()-timedelta(days=1), date_to: date = date.today()):

    # retrieve user information
    dbsession = NewSession()

    date_to = date_to + timedelta(days=1)

    # retrieve measurements
    if register_id >= 0:
        measurements = dbsession.query(Measurement).filter(Measurement.received_at >= date_from).filter(Measurement.received_at <= date_to).filter(Measurement.register_id == register_id).order_by(Measurement.received_at.desc()).all()
    else:
        measurements = dbsession.query(Measurement).filter(Measurement.received_at >= date_from).filter(Measurement.received_at <= date_to).order_by(Measurement.received_at.desc(), Measurement.register_id).all()

    return measurements