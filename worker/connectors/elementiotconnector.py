# imports & globals
from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, desc
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import sessionmaker
from config import logging
from db.models import Measurement, Devices, Direction, SpeedingStatus, TimeSeries
# from logic.common import get_speeding_status

from datetime import datetime
from ast import literal_eval

datetimeformat = '%Y-%m-%dT%H:%M:%S.%fZ'  # 2019-08-26T09:31:41.319216Z,

# Models
Base = declarative_base()


# Devices
class ElementIoTDevice(Base):
    __tablename__ = 'devices'

    id = Column(String(40), primary_key=True)
    parser_id = Column(String(40))  # 68fb21ff-436c-4ba1-8eba-4ece5b6cc6e9
    last_message_at = Column(String(28))
    inserted_at = Column(String(28))  #: 2019-08-13T08:49:19.096588Z
    updated_at = Column(String(28))  # 2019-08-26T09:31:41.319216Z,
    static_location = Column(Boolean)  # false,
    slug = Column(String(255))  #: speedfreak-martinfeld,
    name = Column(String(255))  # Speed-o-mat Martinfeld,
    location = Column(String(512))  #: null,


# Readings
class Reading(Base):
    __tablename__ = 'readings'

    id = Column(String(40), primary_key=True)  # readings id ***
    packet_id = Column(String(40))  # a28000d6-18c7-4099-9bb7-976a3ece92cc,
    device_id = Column(String(40))  # d3829df3-cb83-4691-aae8-9cf70ed85863,
    parser_id = Column(String(40))  # 9ff236ef-e547-4f39-8494-d1fb86321c9e,
    measured_at = Column(String(28))  # 2019-06-24T20:48:09.167897Z,
    inserted_at = Column(String(28))  #: 2019-08-13T08:49:19.096588Z
    location = Column(String(512))  #: null,
    data = Column(String(4096))  #: null,

def init_elementiot_db(MYSQL_DATABASE_URI: str):

    # Create Database if not exists
    if not database_exists(MYSQL_DATABASE_URI):
        create_database(MYSQL_DATABASE_URI)

    # Instanciate database engine
    dbengine = create_engine(MYSQL_DATABASE_URI)

    # Bind Models to Engine, Create Models in DB if not exists
    Base.metadata.create_all(dbengine)

    # Instantiate an return Sessionmakerobject
    Session = sessionmaker(bind=dbengine)

    return Session

def merge_devices_from_elementiot(worker_session, elementiot_session, connector_id):
    """
        pull all (new) speadfreaks from elementiot connector into the speedomat schema
    """

    # get a list of all speedfreak ids in speedomat schema
    deviceids = [r for r, in worker_session.query(Devices.device_extern_id).all()]

    # Iterate over all devices in connector
    elementiotdevices = elementiot_session.query(ElementIoTDevice).all()
    for elementiotdevice in elementiotdevices:
        if elementiotdevice.id not in deviceids:

            # New Device detected
            newdevice = Devices(
                connector_id=connector_id,
                device_extern_id=elementiotdevice.id,
                name=elementiotdevice.name,
                inserted_at=datetime.strptime(elementiotdevice.inserted_at, datetimeformat),
                location_longitude=0,
                location_latitude=0,
                active=False,
                online_ticks_per_hour=0,
                online_ticks=0
            )

            worker_session.add(newdevice)
            worker_session.commit()
            logging.info(f'New device {newdevice.name} with id: {newdevice.device_extern_id} imported from element iot')

    pass

def poll_readings_from_elementiot(worker_session, elementiot_session, device: Devices):
    """
        pull new messages from element iot readings message buffer and import it into
        speedomat use case db
    """
    # Iterate over all messages in connector message buffer
    logging.debug(f'poll data from device {device.name} id:{device.device_extern_id}')
    readings = elementiot_session.query(Reading).filter(Reading.device_id == device.device_extern_id).all()
    for reading in readings:

        # Get Reading Data
        # do we have this message already ?
        measurement = worker_session.query(Measurement).filter(Measurement.device_id == device.device_extern_id).filter(Measurement.measurement_extern_id == reading.id).first()

        if not measurement:

            data = literal_eval(reading.data)
            logging.debug(f'new reading {reading.id} with data: {data} imported from element iot')

            # Instanciate Measurement object
            measurement = Measurement(
                device_id=device.device_id,
                measurement_extern_id=reading.id,
                device_extern_id=device.device_extern_id,
                measured_at=datetime.strptime(reading.measured_at, datetimeformat),
                temp=data.get('temp'),
                so2=data.get('so2'),
                pres=data.get('pres'),
                power=data.get('power'),
                pm25=data.get('pm25'),
                pm10=data.get('pm10'),
                pm1=data.get('pm1'),
                o3=data.get('o3'),
                no2=data.get('no2'),
                hum=data.get('hum', data.get('humi', None)),
                co=data.get('co')
            )
            # Merge to Timeseries
            if merge_measurements_to_datapoints(worker_session, measurement):

                # Add Message to speedomat db
                worker_session.add(measurement)
                worker_session.commit()

                # Delete Message from buffer
                elementiot_session.delete(reading)
                elementiot_session.commit()

        else:
            # Delete Message from buffer
            elementiot_session.delete(reading)
            elementiot_session.commit()



def merge_measurements_to_datapoints(worker_session, measurement: Measurement):
    """
        Merge data in cars_timeseries
    """

    # Get Cars Timeseries Datapoint
    datapoint = worker_session.query(TimeSeries).filter(TimeSeries.device_id == measurement.device_id).filter(TimeSeries.datetime_from <= measurement.measured_at).filter(TimeSeries.datetime_to >= measurement.measured_at).first()
    # Get Device
    device = worker_session.query(Devices).filter(Devices.device_id == measurement.device_id).first()

    if datapoint and device:

        # Update datapoints
        #-----------------------------------------------------------------------------------------------------------
        if measurement.temp:
            datapoint.temp = (datapoint.online_ticks * datapoint.temp + measurement.temp) / (datapoint.online_ticks + 1)

        if measurement.so2:
            datapoint.so2 = (datapoint.online_ticks * datapoint.so2 + measurement.so2) / (datapoint.online_ticks + 1)

        if measurement.pres:
            datapoint.pres = (datapoint.online_ticks * datapoint.pres + measurement.pres) / (datapoint.online_ticks + 1)

        if measurement.pm25:
            datapoint.pm25 = (datapoint.online_ticks * datapoint.pm25 + measurement.pm25) / (datapoint.online_ticks + 1)

        if measurement.pm10:
            datapoint.pm10 = (datapoint.online_ticks * datapoint.pm10 + measurement.pm10) / (datapoint.online_ticks + 1)

        if measurement.pm1:
            datapoint.pm1 = (datapoint.online_ticks * datapoint.pm1 + measurement.pm1) / (datapoint.online_ticks + 1)

        if measurement.o3:
            datapoint.o3 = (datapoint.online_ticks * datapoint.o3 + measurement.o3) / (datapoint.online_ticks + 1)

        if measurement.no2:
            datapoint.no2 = (datapoint.online_ticks * datapoint.no2 + measurement.no2) / (datapoint.online_ticks + 1)

        if measurement.hum:
            datapoint.hum = (datapoint.online_ticks * datapoint.hum + measurement.hum) / (datapoint.online_ticks + 1)

        if measurement.co:
            datapoint.co = (datapoint.online_ticks * datapoint.co + measurement.co) / (datapoint.online_ticks + 1)

        if measurement.power:
            datapoint.power = (datapoint.online_ticks * datapoint.power + measurement.power) / (datapoint.online_ticks + 1)

        datapoint.online_ticks += 1


        # Update Metrics/Momentums
        # -----------------------------------------------------------------
        device.online_ticks += 1

        if not device.first_tick_at:
            device.first_tick_at = measurement.measured_at

        elif device.first_tick_at > measurement.measured_at:
            device.first_tick_at = measurement.measured_at

        if not device.last_tick_at:
            device.last_tick_at = measurement.measured_at

        if device.last_tick_at <= measurement.measured_at:

            device.last_tick_at = measurement.measured_at
            device.temp = measurement.temp
            device.so2 = measurement.so2
            device.pres = measurement.pres
            device.pm25 = measurement.pm25
            device.pm10 = measurement.pm10
            device.pm1 = measurement.pm1
            device.o3 = measurement.o3
            device.no2 = measurement.no2
            device.hum = measurement.hum
            device.co = measurement.co
            device.power = measurement.power


        # Update datapoint and Device commit
        # -------------------------------------------------------------------
        worker_session.commit()

        return True

    else:
        return False
