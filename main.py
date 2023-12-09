from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config import config, logging


from sqlalchemy import func
from db import init_db


from random import randint

# fastapi routers
from routers import api, app

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
    redoc_url=None)


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



# Import fastapi Routes
app.include_router(app.router)
app.include_router(api.router)


# initialize db 
init_db()



