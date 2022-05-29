from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware


from config import config, logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from db import init_db, NewSession
from db.models import User, Device, Measurement
from tools.convert import utc2local, local2utc

import json
import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from random import randint

# MQTT Client
import paho.mqtt.client as mqtt
from parser import message_distributor

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.debug("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(config.MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg:mqtt.MQTTMessage):

    # Parse 
    message_distributor(str(msg.topic), str(msg.payload.decode("utf-8")))

    #Log
    logging.info(f"--- Message received on {msg.topic} -----------------")
    logging.debug(str(msg.payload))

logging.info('----------------------------------------------------------')
logging.info(f'mqtt client start  ....')
logging.debug(f'... running in environment {config}')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set()
client.username_pw_set(username=config.MQTT_USER, password=config.MQTT_PASSWORD)

client.connect(config.MQTT_HOST, config.MQTT_PORT)
client.loop_start()

# Fast Api
logging.info('----------------------------------------------------------')
logging.info(f'fast api start  ....')

description = """
MyKlax API helps you do awesome stuff. 🚀

## Device
You can read your Device Information and Stats.

## Measurements
You can read all Measurements.
"""


app = FastAPI(
    title="MyKlax Api",
    description=description,
    version="0.0.1",
    terms_of_service="https://github.com/omza/klax.dashboard",
    contact={
        "name": "Oliver Meyer",
        "url": "https://omza.de",
        "email": "oliver@omza.de",
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/omza/klax.dashboard/blob/main/LICENSE",
    },    
    redoc_url=None
)

# Templating
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#CORS Support
origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize db 
init_db()


# routes
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request, period: int = 0):

    # retrieve user information
    dbsession = NewSession()
    user =  dbsession.query(User).first()

    #retrieve device data
    device =  dbsession.query(Device).first()

    #retrieve count ticks
    ticks = dbsession.query(Measurement).group_by(Measurement.received_at).count()
    device.ticks = ticks

    # consent management
    cookies_check = True

    # Day Before
    daybefore = (datetime.now() - timedelta(days = 1)).strftime(config.DATEFORMAT)


    if not user or not device:
        return templates.TemplateResponse("error.html", {"request": request, "title": "Dashboard", "messages": []})
    else:
        return templates.TemplateResponse("index.html", {"request": request, 
            "current_user": user, 
            "device": device, 
            "cookies_check": cookies_check, 
            "title": "Dashboard", 
            "period": period, 
            "daybefore": daybefore, 
            "messages": []}
            )

@app.get("/profile", response_class=HTMLResponse, include_in_schema=False)
async def user(request: Request):

    try:
        # retrieve user information
        dbsession = NewSession()
        user =  dbsession.query(User).first()

        #retrieve device data
        device =  dbsession.query(Device).first()

        # consent management
        cookies_check = True

        if not user:
            return templates.TemplateResponse("error.html", {"request": request, "title": "Profil", "messages": []})
        else:
            return templates.TemplateResponse("user.html", {"request": request, "current_user": user, "device": device, "title": "Profil", "messages": [], "cookies_check": cookies_check})

    except:
        return templates.TemplateResponse("error.html", {"request": request, "title": "Profil", "messages": []})



@app.get("/device", response_class=HTMLResponse, include_in_schema=False)
async def device(request: Request):

    try:
        # retrieve user information
        dbsession = NewSession()
        user =  dbsession.query(User).first()

        #retrieve device data
        device =  dbsession.query(Device).first()

        # consent management
        cookies_check = True

        if not user:
            return templates.TemplateResponse("error.html", {"request": request, "title": "Profil", "messages": []})
        else:
            return templates.TemplateResponse("device.html", {"request": request, "current_user": user, "device": device, "title": "Klax Device", "config":config, "messages": [], "cookies_check": cookies_check})

    except:
        return templates.TemplateResponse("error.html", {"request": request, "title": "Profil", "messages": []})

# ------------------------------------------------------
@app.get("/ChartLoadprofile/{period}", include_in_schema=False)
async def ChartLoadprofile(period: int = 0):

    labels = []
    datasets = []
    register_data = []
    charttype = "bar"

    if period == 1:
        # Day Before
    
        start = utc2local(datetime.utcnow(), config.TIMEZONE) - timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=0, microsecond=0)

        dif = int((end-start).total_seconds()/3600) ## time difference in hours
        date_list = [(start + timedelta(hours=x)).strftime("%H:%M") for x in range(dif+1)]

        labels = date_list
        date_list_utc = [(local2utc(start, config.TIMEZONE) + timedelta(hours=x)).strftime("%Y%m%d%H") for x in range(dif+1)]
    

    elif period == 2:
        # last 24 hours
        start = utc2local(datetime.utcnow(), config.TIMEZONE) - timedelta(hours=24)
        start = start.replace(minute=0, second=0, microsecond=0)
        end = utc2local(datetime.utcnow(), config.TIMEZONE).replace(minute=59, second=0, microsecond=0)

        dif = int((end-start).total_seconds()/3600) ## time difference in hours
        date_list = [(start + timedelta(hours=x)).strftime("%d.%m.%Y %H:%M") for x in range(dif+1)]
        date_list_utc = [(local2utc(start, config.TIMEZONE) + timedelta(hours=x)).strftime("%Y%m%d%H") for x in range(dif+1)]

        labels = date_list

    elif period == 3:
        # last 12 Month
        start = utc2local(datetime.utcnow(), config.TIMEZONE) - relativedelta(months=12)
        start = start.replace(day=1,hour=0, minute=0, second=0, microsecond=0)
        end = utc2local(datetime.utcnow(), config.TIMEZONE).replace(day=1,hour=0, minute=0, second=0, microsecond=0)

        dif = 11
        date_list = [(start + relativedelta(months=x)).strftime("%b %Y") for x in range(dif+1)]
        date_list_utc = [(start + relativedelta(months=x)).strftime("%Y%m") for x in range(dif+1)]

        labels = date_list


    else:
        # last 30 Days
        charttype = "line"
        start = utc2local(datetime.utcnow(), config.TIMEZONE) - timedelta(days=30)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = utc2local(datetime.utcnow(), config.TIMEZONE).replace(hour=0, minute=59, second=0, microsecond=0)

        dif = int((end-start).total_seconds()/86400) ## time difference in days
        date_list = [(start + timedelta(days=x)).strftime("%d.%m.%Y") for x in range(dif+1)]
        #date_list_utc = [(local2utc(start, config.TIMEZONE) + timedelta(days=x)).strftime("%Y%m%d") for x in range(dif+1)]
        date_list_utc = date_list
        labels = date_list


    """
    select device_id, register_id, strftime('%Y%m%d%H',start_at) label, sum(load) from timeseries where device_id = 1 and register_id = 0 group by device_id, register_id, label    
    """

    # retrieve user information
    dbsession = NewSession()
    user =  dbsession.query(User).first()

    #retrieve device data
    device =  dbsession.query(Device).first()


    if device:

        # Register 0
        if device.register0_Active:
            rgb = "78, 223, 78"
            register_id = 0
            register_data = []

            if 1 <= period <= 2:
                # Hours
                sql = f"select strftime('%Y%m%d%H',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
               
            elif period == 3:
                # Month
                sql = f"select strftime('%Y%m',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
            else:
                # days
                sql = f"select strftime('%d.%m.%Y',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label" 

            logging.debug(sql)

            resultset = [dict(row) for row in dbsession.execute(sql)]

            if resultset:
                for label in date_list_utc:

                    row = list(filter(lambda item: item['label'] == label, resultset))
                    if row:
                        row = dict(row[0])
                        register_data.append(row['load'])

                    else:
                        register_data.append(None)

                # Register
                dataset = {
                    "label": device.register0_name,
                    "backgroundColor": "rgba(" + rgb + ", 1)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.5)",
                    "borderColor": "rgba(" + rgb + ", 1)",                    
                    "data": register_data
                }
                datasets.append(dataset)

        # Register 1
        if device.register1_Active:
            rgb = "78, 78, 223"
            register_id = 1
            register_data = []

            if 1 <= period <= 2:
                # Hours
                sql = f"select strftime('%Y%m%d%H',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
               
            elif period == 3:
                # Month
                sql = f"select strftime('%Y%m',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
            else:
                # days
                sql = f"select strftime('%d.%m.%Y',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label" 
                
            logging.debug(sql)

            resultset = [dict(row) for row in dbsession.execute(sql)]

            if resultset:
                for label in date_list_utc:

                    row = list(filter(lambda item: item['label'] == label, resultset))
                    if row:
                        row = dict(row[0])
                        register_data.append(row['load'])

                    else:
                        register_data.append(None)

                # Register
                dataset = {
                    "label": device.register1_name,
                    "backgroundColor": "rgba(" + rgb + ", 1)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.5)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.append(dataset)

        # Register 2
        if device.register2_Active:
            rgb = "78, 78, 223"
            register_id = 2
            register_data = []

            if 1 <= period <= 2:
                # Hours
                sql = f"select strftime('%Y%m%d%H',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
               
            elif period == 3:
                # Month
                sql = f"select strftime('%Y%m',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
            else:
                # days
                sql = f"select strftime('%d.%m.%Y',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label" 
                
            logging.debug(sql)

            resultset = [dict(row) for row in dbsession.execute(sql)]

            if resultset:
                for label in date_list_utc:

                    row = list(filter(lambda item: item['label'] == label, resultset))
                    if row:
                        row = dict(row[0])
                        register_data.append(row['load'])

                    else:
                        register_data.append(None)

                # Register
                dataset = {
                    "label": device.register2_name,
                    "backgroundColor": "rgba(" + rgb + ", 1)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.5)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.append(dataset)

        # Register 3
        if device.register3_Active:
            rgb = "78, 78, 223"
            register_id = 3
            register_data = []

            if 1 <= period <= 2:
                # Hours
                sql = f"select strftime('%Y%m%d%H',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
               
            elif period == 3:
                # Month
                sql = f"select strftime('%Y%m',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label"                
            else:
                # days
                sql = f"select strftime('%d.%m.%Y',start_at) label, sum(load) load from timeseries where device_id = {device.device_id} and register_id = {register_id} and date(start_at) >= '{start.strftime('%Y-%m-%d')}' group by device_id, register_id, label" 
                
            logging.debug(sql)

            resultset = [dict(row) for row in dbsession.execute(sql)]
            if resultset:
                for label in date_list_utc:

                    row = list(filter(lambda item: item['label'] == label, resultset))
                    if row:
                        row = dict(row[0])
                        register_data.append(row['load'])

                    else:
                        register_data.append(None)

                # Register
                dataset = {
                    "label": device.register3_name,
                    "backgroundColor": "rgba(" + rgb + ", 1)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.5)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.append(dataset)




    else:

        for label in labels:
            register_data.append(None)

        dataset = {
            "label": "no Klax",
            "backgroundColor": "rgba(78, 78, 223, 1)",
            "hoverBackgroundColor": "rgba(78, 78, 223, 0.5)",
            "borderColor": "rgba(78, 78, 223, 1)",                   
            "data": register_data
        }
        datasets.append(dataset)



    timeseries = {
        "labels": labels,
        "datasets": datasets
    }

    # Return Timeseries and charttype (bar or line)
    chartdata = {
        "type": charttype,
        "timeseries": timeseries
    }


    return chartdata


@app.get("/api/device")
async def read_device():

    # retrieve user information
    dbsession = NewSession()

    #retrieve device data
    device =  dbsession.query(Device).first()

    return device

@app.get("/api/measurements")
async def read_measurements(register_id: int = -1, date_from: date = date.today()-timedelta(days=1), date_to: date = date.today()):

    # retrieve user information
    dbsession = NewSession()

    date_to = date_to + timedelta(days=1)

    # retrieve measurements
    if register_id >= 0:
        measurements = dbsession.query(Measurement).filter(Measurement.received_at >= date_from).filter(Measurement.received_at <= date_to).filter(Measurement.register_id == register_id).order_by(Measurement.received_at.desc()).all()
    else:
        measurements = dbsession.query(Measurement).filter(Measurement.received_at >= date_from).filter(Measurement.received_at <= date_to).order_by(Measurement.received_at.desc(), Measurement.register_id).all()

    return measurements