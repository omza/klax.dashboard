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

import json
import time
from datetime import datetime, date, timedelta

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

app = FastAPI()

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
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, period: int = 0):

    # retrieve user information
    dbsession = NewSession()
    user =  dbsession.query(User).first()

    #retrieve device data
    device =  dbsession.query(Device).first()

    #retrieve count ticks
    ticks = dbsession.query(Measurement).group_by(Measurement.received_at).count()
    print(ticks)
    device.ticks = ticks

    # consent management
    cookies_check = True

    if not user or not device:
        return templates.TemplateResponse("error.html", {"request": request, "title": "klax dashboard", "messages": []})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "current_user": user, "device": device, "cookies_check": cookies_check, "title": "Klax Dashboard", "period": period, "messages": []})


@app.get("/profile", response_class=HTMLResponse)
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



@app.get("/device", response_class=HTMLResponse)
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
@app.get("/ChartLoadprofile/{period}")
async def ChartLoadprofile(period: int = 0):

    base = datetime.utcnow()
    base = base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
   
    """
    metrics = {"labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
              "datasets": [
                {
                "label": "1.8.0",
                "lineTension": 0.3,
                "backgroundColor": "rgba(78, 115, 223, 0.05)",
                "borderColor": "rgba(78, 115, 223, 1)",
                "pointRadius": 3,
                "pointBackgroundColor": "rgba(78, 115, 223, 1)",
                "pointBorderColor": "rgba(78, 115, 223, 1)",
                "pointHoverRadius": 3,
                "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
                "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
                "pointHitRadius": 10,
                "pointBorderWidth": 2,
                "data": [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 25000, 40000]}, 
              {
                "label": "2.8.0",
                "lineTension": 0.3,
                "backgroundColor": "rgba(78, 223, 78, 0.05)",
                "borderColor": "rgba(78, 223, 78, 1)",
                "pointRadius": 3,
                "pointBackgroundColor": "rgba(78, 223, 78, 1)",
                "pointBorderColor": "rgba(78, 223, 78, 1)",
                "pointHoverRadius": 3,
                "pointHoverBackgroundColor": "rgba(78, 223, 78, 1)",
                "pointHoverBorderColor": "rgba(78, 223, 78, 1)",
                "pointHitRadius": 10,
                "pointBorderWidth": 2,
                "data": [0, 5000, 5000, 10000, 20000, 10000, 10000, 20000, 15000, 20000, 15000, 10000]}],
            }
            """
            
    # Humidity
    datasets = []
    dataset = {
        "label": "1.8.0",
        "lineTension": 0.3,
        "backgroundColor": "rgba(78, 115, 223, 0.05)",
        "borderColor": "rgba(78, 115, 223, 1)",
        "pointRadius": 3,
        "pointBackgroundColor": "rgba(78, 115, 223, 1)",
        "pointBorderColor": "rgba(78, 115, 223, 1)",
        "pointHoverRadius": 3,
        "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
        "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
        "pointHitRadius": 10,
        "pointBorderWidth": 2,
        'spanGaps': True,
        "data": [0, 5000, 5000, 10000, 20000, 10000, 10000, 20000, 15000, 20000, 15000, 10000]
    }
    datasets.append(dataset)

    dataset = {
        "label": "2.8.0",
        "lineTension": 0.3,
        "backgroundColor": "rgba(78, 223, 78, 0.05)",
        "borderColor": "rgba(78, 223, 78, 1)",
        "pointRadius": 3,
        "pointBackgroundColor": "rgba(78, 223, 78, 1)",
        "pointBorderColor": "rgba(78, 223, 78, 1)",
        "pointHoverRadius": 3,
        "pointHoverBackgroundColor": "rgba(78, 223, 78, 1)",
        "pointHoverBorderColor": "rgba(78, 223, 78, 1)",
        "pointHitRadius": 10,
        "pointBorderWidth": 2,
        'spanGaps': True,
        "data": [0, 5000, 5000, 10000, None, 10000, None, 20000, 15000, None, 15000, 10000]
    }
    datasets.append(dataset)

    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    metrics = {
        "labels": labels,
        "datasets": datasets
    }


    

    return metrics
