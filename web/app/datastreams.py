# Imports & Globals
from flask import Response, jsonify, abort
from app import app, db, logging
from app.models import Device, Measurement

import json
#import random
import time
from datetime import datetime, date, timedelta

from app.logic import utc2local_str, utc2local, utc2local_date_str, random_color_rgba

# ------------------------------------------------------
@app.route('/devices/chart-datasets-day/<device_id>')
@app.route('/chart-datasets-day')
def chart_metrics_day(device_id=None):

    try:
        base = datetime.utcnow()
        base = base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        labels = [utc2local_str(base - timedelta(hours=24 - x)) for x in range(24)]
        dashboard = False

        if device_id:
            devices = Devices.query.filter(Devices.active).filter(Devices.device_id == device_id).all()

        else:
            devices = Devices.query.filter(Devices.active).all()
            dashboard = True

        for device in devices:

            # Labels
            if not dashboard:
                base = device.last_tick_at
                base = base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                labels = [utc2local_str(base - timedelta(hours=24 - x)) for x in range(24)]

            # Chart Gas Concentrations
            o3_data = []
            so2_data = []
            no2_data = []
            co_data = []

            # Chart particulate-matter Concentrations
            pm25_data = []
            pm10_data = []
            pm1_data = []

            # Charts Environment
            temp_data = []
            hum_data = []
            pres_data = []

            sql = "SELECT ADDDATE(DATE(measured_at), INTERVAL HOUR(measured_at) HOUR) datetime_from, " \
                "ROUND(MAX(so2),5) so2, ROUND(MAX(o3),5) o3, ROUND(MAX(no2),5) no2, ROUND(MAX(co),5) co, " \
                "ROUND(MAX(pm25),5) pm25, ROUND(MAX(pm10),5) pm10, ROUND(MAX(pm1),5) pm1, " \
                "ROUND(MAX(temp),2) temp, ROUND(MAX(pres),3) pres, ROUND(MAX(hum),5) hum " \
                "FROM " \
                "measurements WHERE device_id = " + str(device.device_id) + " GROUP BY device_id, DATE(measured_at), HOUR(measured_at) ORDER BY  DATE(measured_at) DESC, HOUR(measured_at) DESC LIMIT 24"
            resultset = [dict(row) for row in db.engine.execute(sql)]
            logging.debug(resultset)

            if resultset:
                for label in labels:
                    row = list(filter(lambda item: utc2local_str(item['datetime_from']) == label, resultset))
                    if row:
                        row = dict(row[0])
                        o3_data.append(row['o3'])
                        so2_data.append(row['so2'])
                        no2_data.append(row['no2'])
                        co_data.append(row['co'])
                        pm25_data.append(row['pm25'])
                        pm10_data.append(row['pm10'])
                        pm1_data.append(row['pm1'])
                        temp_data.append(row['temp'])
                        pres_data.append(row['pres'])
                        hum_data.append(row['hum'])

                    else:
                        o3_data.append(None)
                        so2_data.append(None)
                        no2_data.append(None)
                        co_data.append(None)
                        pm25_data.append(None)
                        pm10_data.append(None)
                        pm1_data.append(None)
                        temp_data.append(None)
                        pres_data.append(None)
                        hum_data.append(None)

            else:
                for label in labels:
                    o3_data.append(None)
                    so2_data.append(None)
                    no2_data.append(None)
                    co_data.append(None)
                    pm25_data.append(None)
                    pm10_data.append(None)
                    pm1_data.append(None)
                    temp_data.append(None)
                    pres_data.append(None)
                    hum_data.append(None)


            # Prepare datasets for Gas Concentration chart
            datasets = []
            o3 = {
                'label': 'Ozon',
                'stack': device.name,
                'borderColor': 'rgb(98, 178, 46, 1)',
                'backgroundColor': 'rgba(98, 178, 46, 1)',
                'barThickness': 'flex',
                'data': o3_data
            }

            so2 = {
                'label': 'Schwefeldioxid',
                'stack': device.name,
                'borderColor': 'rgb(255, 230, 0, 1)',
                'backgroundColor': 'rgba(255, 230, 0, 1)',
                'barThickness': 'flex',
                'data': so2_data
            }

            no2 = {
                'label': 'Stickstoffdioxid',
                'stack': device.name,
                'borderColor': 'rgb(237, 22, 12, 1)',
                'backgroundColor': 'rgba(237, 22, 12, 1)',
                'barThickness': 'flex',
                'data': no2_data
            }

            co = {
                'label': 'Kohlenmonoxid',
                'stack': device.name,
                'borderColor': 'rgb(0, 0, 0, 1)',
                'backgroundColor': 'rgba(0, 0, 0, 1)',
                'barThickness': 'flex',
                'data': co_data
            }

            datasets.append(o3)
            # datasets.append(so2)
            datasets.append(no2)
            # datasets.append(co)

            if datasets:
                # Prepare Chart dict
                chart_gas = {
                    'labels': labels,
                    'datasets': datasets
                }

            # Prepare Particulary Matter Chart
            datasets = []
            pm25 = {
                'label': 'Feinstaub 25µm',
                # 'stack': device.name,
                'borderColor': 'rgb(98, 178, 46, 1)',
                'backgroundColor': 'rgba(98, 178, 46, 0.1)',
                'spanGaps': True,
                'fill': False,
                'data': pm25_data
            }

            pm10 = {
                'label': 'Feinstaub 10µm',
                # 'stack': device.name,
                'borderColor': 'rgb(255, 230, 0, 1)',
                'backgroundColor': 'rgba(255, 230, 0, 0.1)',
                'spanGaps': True,
                'data': pm10_data
            }

            pm1 = {
                'label': 'Feinstaub 1µm',
                # 'stack': device.name,
                'borderColor': 'rgb(237, 22, 12, 1)',
                'backgroundColor': 'rgba(237, 22, 12, 0.1)',
                'spanGaps': True,
                'data': pm1_data
            }

            datasets.append(pm25)
            datasets.append(pm10)
            datasets.append(pm1)

            if datasets:
                # Prepare Chart dict
                chart_pm = {
                    'labels': labels,
                    'datasets': datasets
                }

            # prepare environment Metrics
            # ---------------------------------------------------
            # Temp
            dataset = {
                'label': device.name,
                'borderColor': 'rgba(0, 0, 255, 1)',
                'backgroundColor': 'rgba(0, 0, 255, 0.1)',
                'spanGaps': True,
                'data': temp_data
            }

            chart_temp = {
                'labels': labels,
                'datasets': [dataset]
            }

            # Pressure
            dataset = {
                'label': device.name,
                'borderColor': 'rgba(0, 0, 255, 1)',
                'backgroundColor': 'rgba(0, 0, 255, 0.1)',
                'spanGaps': True,
                'data': pres_data
            }

            chart_pres = {
                'labels': labels,
                'datasets': [dataset]
            }

            # Humidity
            dataset = {
                'label': device.name,
                'borderColor': 'rgba(0, 0, 255, 1)',
                'backgroundColor': 'rgba(0, 0, 255, 0.1)',
                'spanGaps': True,
                'data': hum_data
            }

            chart_hum = {
                'labels': labels,
                'datasets': [dataset]
            }

        metrics = {
            'chart_gas': chart_gas,
            'chart_pm': chart_pm,
            'chart_temp': chart_temp,
            'chart_pres': chart_pres,
            'chart_hum': chart_hum
        }

        if metrics:
            return jsonify(metrics), 200

        else:
            return jsonify({'error': 'Ressource not found'}), 404

    except:
        return jsonify({'error': 'Internal Server error'}), 500