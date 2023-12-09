from fastapi import APIRouter

from fastapi import  Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import func
from db import NewSession
from db.models import User, Device, Measurement
from tools.convert import utc2local, local2utc

import json
import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from config import config, logging

router = APIRouter()

# Templating
router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# routes
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
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

@router.get("/profile", response_class=HTMLResponse, include_in_schema=False)
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



@router.get("/device", response_class=HTMLResponse, include_in_schema=False)
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
@router.get("/ChartLoadprofile/{period}", include_in_schema=False)
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
                        register_data.routerend(row['load'])

                    else:
                        register_data.routerend(None)

                # Register
                dataset = {
                    "label": device.register0_name,
                    "backgroundColor": "rgba(" + rgb + ", 0.5)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.3)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.routerend(dataset)

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
                        register_data.routerend(row['load'])

                    else:
                        register_data.routerend(None)

                # Register
                dataset = {
                    "label": device.register1_name,
                    "backgroundColor": "rgba(" + rgb + ", 0.5)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.3)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.routerend(dataset)

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
                        register_data.routerend(row['load'])

                    else:
                        register_data.routerend(None)

                # Register
                dataset = {
                    "label": device.register2_name,
                    "backgroundColor": "rgba(" + rgb + ", 0.5)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.3)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.routerend(dataset)

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
                        register_data.routerend(row['load'])

                    else:
                        register_data.routerend(None)

                # Register
                dataset = {
                    "label": device.register3_name,
                    "backgroundColor": "rgba(" + rgb + ", 0.5)",
                    "hoverBackgroundColor": "rgba(" + rgb + ",0.3)",
                    "borderColor": "rgba(" + rgb + ", 1)",                   
                    "data": register_data
                }
                datasets.routerend(dataset)




    else:

        for label in labels:
            register_data.routerend(None)

        dataset = {
            "label": "no Klax",
            "backgroundColor": "rgba(78, 78, 223, 0.5)",
            "hoverBackgroundColor": "rgba(78, 78, 223, 0.3)",
            "borderColor": "rgba(78, 78, 223, 1)",                   
            "data": register_data
        }
        datasets.routerend(dataset)



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

