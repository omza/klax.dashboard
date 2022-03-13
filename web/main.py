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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize db 
init_db()


# routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

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