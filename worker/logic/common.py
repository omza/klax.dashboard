from datetime import datetime, timedelta
from db.models import TimeSeries, Devices, DayType, Connector, ConnectorType
from sqlalchemy import func
from sqlalchemy.orm import Session
from config import logging, config
from db import init_worker_db
from connectors.elementiotconnector import init_elementiot_db, merge_devices_from_elementiot, poll_readings_from_elementiot

def get_daytype(device: Devices, day):
    """
        determine a DayType depending on Speedfreak Calendar and the Day given
    """

    # determine season
    md = day.month * 100 + day.day

    if ((md > 320) and (md < 621)):
        daytype = 20  # spring
    elif ((md > 620) and (md < 923)):
        daytype = 10  # summer
    elif ((md > 922) and (md < 1223)):
        daytype = 20  # fall
    else:
        daytype = 30  # winter

    # determine weekdays
    if 0 <= day.weekday() <= 4:
        daytype = daytype + 1

    elif day.weekday() == 5:
        daytype = daytype + 2

    else:
        daytype = daytype + 3

    return DayType(daytype)

def rollout_timeseries(worker_session: Session, device: Devices):
    """
        create datapoints each hour minutes for car measurements for
    """

    # determine date_to
    max_date_to = datetime.utcnow() + timedelta(days=2)
    max_date_to = max_date_to.replace(hour=0, minute=0, second=0, microsecond=0)

    # determine date_from
    date_from = worker_session.query(func.max(TimeSeries.datetime_to)).filter(TimeSeries.device_id == device.device_id).scalar()

    if not date_from:
        # no Datapoints available
        date_from = device.inserted_at.replace(minute=0, second=0, microsecond=0)

    while date_from <= max_date_to:

        date_to = date_from + timedelta(hours=1) # Raster
        daytype = get_daytype(device, date_from)

        datapoint = TimeSeries(
            device_id=device.device_id,
            datetime_from=date_from,
            datetime_to=date_to,
            daytype_id=daytype.value,
            online_ticks=0
        )
        worker_session.add(datapoint)

        date_from = date_from + timedelta(hours=1)
        date_to = date_to + timedelta(hours=1)

    worker_session.commit()
    return

def rollout_timeseries_all():
    """
        create datapoints each hour minutes for car measurements for
    """

    worker_sessionmaker = init_worker_db()
    worker_session = worker_sessionmaker()

    devices = worker_session.query(Devices).all()

    for device in devices:

        logging.debug(f'starting rollout timeseries for {device.name}...')

        # determine date_to
        max_date_to = datetime.utcnow() + timedelta(days=2)
        max_date_to = max_date_to.replace(hour=0, minute=0, second=0, microsecond=0)

        # determine date_from
        date_from = worker_session.query(func.max(TimeSeries.datetime_to)).filter(TimeSeries.device_id == device.device_id).scalar()

        if not date_from:
            # no Datapoints available
            date_from = device.inserted_at.replace(minute=0, second=0, microsecond=0)

        index = 0
        while date_from <= max_date_to:

            date_to = date_from + timedelta(hours=1) # Raster
            daytype = get_daytype(device, date_from)

            datapoint = TimeSeries(
                device_id=device.device_id,
                datetime_from=date_from,
                datetime_to=date_to,
                daytype_id=daytype.value,
                online_ticks=0
            )
            
            worker_session.add(datapoint)
            worker_session.commit()

            date_from = date_from + timedelta(hours=1)
            date_to = date_to + timedelta(hours=1)

            index += 1
            
    
        logging.debug(f'rollout timeseries for {device.name} done! {index} datapoints added')

    worker_session.close()
    return

def create_demo_objects(worker_session: Session):
    """
        Create Demo speedfreak
    """

    # No Connector no Demo speedfreak!
    connector = worker_session.query(Connector).first()

    if connector:

        # If there are speedfreaks do nothing
        devices = worker_session.query(Devices).all()

        if not devices:

            speedfreak = Devices(
                connector_id=connector.connector_id,
                device_extern_id='1',
                name='Demo',
                inserted_at=datetime.utcnow(),
                location_longitude=1, location_latitude=1,
                active=False,
                online_ticks_per_hour=60,
                online_ticks=0)

            worker_session.add(speedfreak)
            worker_session.commit()

def poll_readings():

    logging.info(f'poll readings from devices...')
    worker_sessionmaker = init_worker_db()
    worker_session = worker_sessionmaker()
    devices = worker_session.query(Devices).filter(Devices.active).all()
    for device in devices:

        # Test Connector Type
        connector = worker_session.query(Connector).filter(Connector.connector_id == device.connector_id).first()
        if connector.connector_type == ConnectorType.ELEMENTIOT.value:

            # Connect to Connector Database
            elementiot_db_uri = config.MYSQL_DATABASE_BASE_URI
            if elementiot_db_uri.endswith('/'):
                elementiot_db_uri = elementiot_db_uri + connector.connector_database
            else:
                elementiot_db_uri = elementiot_db_uri + '/' + connector.connector_database

            elementiot_sessionmaker = init_elementiot_db(elementiot_db_uri)
            elementiot_session = elementiot_sessionmaker()

            # poll readings
            poll_readings_from_elementiot(
                worker_session,
                elementiot_session,
                device)
            
            elementiot_session.close()
    
    worker_session.close()
    logging.info(f'poll readings from devices done!')

def merge_devices():

    logging.info(f'merging devices...')
    worker_sessionmaker = init_worker_db()
    worker_session = worker_sessionmaker()
    connectors = worker_session.query(Connector).all()
    for connector in connectors:

        # Test Connector Type
        if connector.connector_type == ConnectorType.ELEMENTIOT.value:

            # Connect to Connector Database
            elementiot_db_uri = config.MYSQL_DATABASE_BASE_URI
            if elementiot_db_uri.endswith('/'):
                elementiot_db_uri = elementiot_db_uri + connector.connector_database
            else:
                elementiot_db_uri = elementiot_db_uri + '/' + connector.connector_database

            elementiot_sessionmaker = init_elementiot_db(elementiot_db_uri)
            elementiot_session = elementiot_sessionmaker()

            # retrieve at startup and schedule merge speadfreaks
            merge_devices_from_elementiot(
                worker_session,
                elementiot_session,
                connector.connector_id)

            elementiot_session.close()
    
    worker_session.close()
    logging.info(f'merging devices done!')

"""
def classify_measurements(worker_session: Session):

        (re) classifiy all measurements from speedfreaks wich are changed in speedlimits and speeding categories
        filter = rebuild_until_measurement_id
    speedfreaks = worker_session.query(Speedfreak).filter(Speedfreak.active).filter(Speedfreak.rebuild_until_measurement_id > 0).all()
    for speedfreak in speedfreaks:

        # update measurements
        logging.debug(f'start reclassify {speedfreak.name}...')

        # update speeding
        sql = 'UPDATE measurements SET speeding = speed - ' + str(speedfreak.speedlimit) + ', speeding_status = 0 WHERE speedfreak_id = ' + str(speedfreak.speedfreak_id) + ' and speed >= 0'
        worker_session.execute(sql)
        logging.debug(f'done reclassify speeding!')

        # reclassifiy Deadslow = <= 10% Speedlimit
        deadslowthreshold = int(round(speedfreak.speedlimit / 10, 0))
        sql = 'UPDATE measurements SET speeding_status = ' + SpeedingStatus.DEADSLOW.value + ' WHERE speedfreak_id = ' + str(speedfreak.speedfreak_id) + ' and speed  <= ' + str(deadslowthreshold) + ' and speeding_status = 0'
        worker_session.execute(sql)
        logging.debug(f'done reclassify deadslows!')

        # reclassifiy Alarm
        sql = 'UPDATE measurements SET speeding_status = ' + SpeedingStatus.ALARM.value + ' WHERE speedfreak_id = ' + str(speedfreak.speedfreak_id) + ' and speeding  >= ' + str(speedfreak.speed_alarm_threshold) + ' and speeding_status = 0'
        worker_session.execute(sql)
        logging.debug(f'done reclassify alarms!')

        # reclassifiy Warning
        sql = 'UPDATE measurements SET speeding_status = ' + SpeedingStatus.WARNING.value + ' WHERE speedfreak_id = ' + str(speedfreak.speedfreak_id) + ' and speeding  >= ' + str(speedfreak.speed_warning_threshold) + ' and speeding_status = 0'
        worker_session.execute(sql)
        logging.debug(f'done reclassify warnings!')

        # update car_timeseries

        # alarms
        sql = "UPDATE car_timeseries AS T INNER JOIN " \
            "(SELECT T2.speedfreak_id, T2.datetime_from, T2.datetime_to, COUNT(M2.measurement_id) AS alarms " \
            "FROM car_timeseries AS T2 JOIN measurements AS M2 " \
            "ON T2.speedfreak_id = M2.speedfreak_id AND M2.measured_at BETWEEN T2.datetime_from AND T2.datetime_to " \
            "WHERE M2.speeding_status = " + SpeedingStatus.ALARM.value + " GROUP BY T2.speedfreak_id, T2.datetime_from, T2.datetime_to) AS M " \
            "ON T.speedfreak_id = M.speedfreak_id AND M.datetime_from = T.datetime_from AND M.datetime_to = T.datetime_to " \
            "SET T.speed_alarms = M.alarms " \
            "WHERE T.speedfreak_id = " + str(speedfreak.speedfreak_id)
        worker_session.execute(sql)
        logging.debug(f'done reclassify car_timeseries alarms!')

        # deadslows
        sql = "UPDATE car_timeseries AS T INNER JOIN " \
            "(SELECT T2.speedfreak_id, T2.datetime_from, T2.datetime_to, COUNT(M2.measurement_id) AS deadslows " \
            "FROM car_timeseries AS T2 JOIN measurements AS M2 " \
            "ON T2.speedfreak_id = M2.speedfreak_id AND M2.measured_at BETWEEN T2.datetime_from AND T2.datetime_to " \
            "WHERE M2.speeding_status = " + SpeedingStatus.DEADSLOW.value + " GROUP BY T2.speedfreak_id, T2.datetime_from, T2.datetime_to) AS M " \
            "ON T.speedfreak_id = M.speedfreak_id AND M.datetime_from = T.datetime_from AND M.datetime_to = T.datetime_to " \
            "SET T.speed_deadslows = M.deadslows " \
            "WHERE T.speedfreak_id = " + str(speedfreak.speedfreak_id)
        worker_session.execute(sql)
        logging.debug(f'done reclassify car_timeseries deadslows!')

        # warnings
        sql = "UPDATE car_timeseries AS T INNER JOIN " \
            "(SELECT T2.speedfreak_id, T2.datetime_from, T2.datetime_to, COUNT(M2.measurement_id) AS warnings " \
            "FROM car_timeseries AS T2 JOIN measurements AS M2 " \
            "ON T2.speedfreak_id = M2.speedfreak_id AND M2.measured_at BETWEEN T2.datetime_from AND T2.datetime_to " \
            "WHERE M2.speeding_status = " + SpeedingStatus.WARNINGS.value + " GROUP BY T2.speedfreak_id, T2.datetime_from, T2.datetime_to) AS M " \
            "ON T.speedfreak_id = M.speedfreak_id AND M.datetime_from = T.datetime_from AND M.datetime_to = T.datetime_to " \
            "SET T.speed_warnings = M.warnings " \
            "WHERE T.speedfreak_id = " + str(speedfreak.speedfreak_id)
        worker_session.execute(sql)
        logging.debug(f'done reclassify car_timeseries warnings!')

        # normals
        sql = 'UPDATE car_timeseries SET speed_normals = cars_total - speed_alarms - speed_deadslows - speed_warnings WHERE speedfreak_id = ' + str(speedfreak.speedfreak_id)
        worker_session.execute(sql)

        # update speedfreak metrics
        #
        sql = "UPDATE speedfreaks s INNER JOIN " \
            "(SELECT speedfreak_id, SUM(speed_alarms) AS alarms, sum(speed_deadslows) as deadslows, sum(speed_normals) as normals, sum(speed_warnings) as warnings " \
            "FROM car_timeseries GROUP BY speedfreak_id) t " \
            "ON s.speedfreak_id = t.speedfreak_id " \
            "SET s.speed_alarms = t.alarms, s.speed_deadslows = t.deadslows, s.speed_normals = t.normals, s.speed_warnings = t.warnings " \
            "WHERE s.speedfreak_id = " + str(speedfreak.speedfreak_id)
        worker_session.execute(sql)

        speedfreak.rebuild_until_measurement_id = 0
        worker_session.commit()
        logging.debug(f'done reclassify {speedfreak.name}!')
"""