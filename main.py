from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from config import config, logging

from sqlalchemy.orm import sessionmaker
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
async def index(request: Request):

    logging.debug(request.headers) 
    
    # retrieve user information
    dbsession = NewSession()
    user =  dbsession.query(User).first()

    #retrieve device data
    device =  dbsession.query(Device).first()

    # consent management
    cookies_check = True

    if not user:
        return templates.TemplateResponse("error.html", {"request": request, "title": "klax dashboard", "messages": []})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "current_user": user, "device": device, "cookies_check": cookies_check, "title": "Klax Dashboard", "messages": []})


@app.get("/profile", response_class=HTMLResponse)
async def user(request: Request):

    logging.debug(request.headers) 

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

@app.get("/device", response_class=HTMLResponse)
async def device(request: Request):

    # retrieve user information
    dbsession = NewSession()
    user =  dbsession.query(User).first()

    #retrieve device data
    device =  dbsession.query(Device).first()

    # consent management
    cookies_check = True

    if not user:
        return templates.TemplateResponse("error.html", {"request": request, "title": "Klax Device", "messages": []})
    else:
        return templates.TemplateResponse("device.html", {"request": request, "current_user": user, "device": device, "title": "Klax Device", "messages": [], "cookies_check": cookies_check})


# ------------------------------------------------------
@app.route('/devices/chart-datasets-day/<device_id>')
@app.route('/chart-datasets-day')
def chart_metrics_day(device_id=None):

    try:
        base = datetime.utcnow()
        base = base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        #labels = [utc2local_str(base - timedelta(hours=24 - x)) for x in range(24)]
        dashboard = False

        metrics = {
            'chart_gas': "10",
            'chart_pm': "20",
            'chart_temp': "30",
            'chart_pres': "40",
            'chart_hum': "50"
        }

        if metrics:
            return json.dumps(metrics), 200

        else:
            return json.dumps({'error': 'Ressource not found'}), 404

    except:
        return json.dumps({'error': 'Internal Server error'}), 500