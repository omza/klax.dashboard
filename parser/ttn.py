from datetime import datetime, timedelta
from pydoc_data.topics import topics
from db import NewSession
from db.models import Device, Loadprofile, Measurement
from sqlalchemy import func, create_engine
from sqlalchemy.orm import Session, sessionmaker
from config import logging, config
import json
import iso8601


"""
    ttn Simulate Message Payload to FPort 3:
    04454111030A0149534B0004A4E1CF01110F47E6780047E6780047E6780047E6780001130F46ABE00046ABE00046A4100046A41000

"""


def ttn_klax_parser(topic: str, payload: str):
    """ Parse the klaxmessage out of the mqtt message payload sent via ttn 
        its JSON
        klax 2.0 devices are onboarded including a payload decoder so no need to decode the klax payload
        its all in the ttn message payload json
    """

    # deserialize and Parse JSON
    message = json.loads(payload)

    end_device_ids = message["end_device_ids"]
    received_at = iso8601.parse_date(message["received_at"])

    message = message["uplink_message"]
    

    # Measurements from klax only on lorawan Port 3 (klax 2.0. Spec)
    # ignore uplinks on other ports
    if message["f_port"] == 3:

        message = message["decoded_payload"]
        header = message["header"]
        payloads = message["payloads"]

        # Instanciate database engine
        #dbengine = create_engine(config.MYSQL_DATABASE_URI, pool_recycle=config.SQLALCHEMY_POOL_RECYCLE, connect_args={'check_same_thread': False})
        #dbsessionmaker = sessionmaker(bind=dbengine)
        dbsession = NewSession()

        # process to db
        if not (not end_device_ids or not header or not received_at):

            device = dbsession.query(Device).filter_by(device_extern_id=end_device_ids["device_id"]).first()
            if not device:

                device = Device(
                    device_extern_id = end_device_ids["device_id"],
                    inserted_at = datetime.utcnow(),

                    dev_eui = end_device_ids["dev_eui"],
                    batteryPerc = header["batteryPerc"],
                    configured = header["configured"],
                    connTest =   header["connTest"],
                    deviceType = header["deviceType"],
                    meterType = header["meterType"],
                    version = header["version"],

                    register0_name = "1.8.0",
                    register0_Active = False,
                    register1_name = "2.8.0",
                    register1_Active = False,                    
                    register2_name = "OFF",
                    register2_Active = False,                    
                    register3_name = "OFF",
                    register3_Active = False,

                    lastseen_at = received_at,
                    mqtt_topic = topic
                )
            
                dbsession.add(device)
                dbsession.commit()

            else:
                
                device.dev_eui = end_device_ids["dev_eui"]
                device.batteryPerc = header["batteryPerc"]
                device.configured = header["configured"]
                device.connTest =   header["connTest"]
                device.deviceType = header["deviceType"]
                device.meterType = header["meterType"]
                device.version = header["version"]
                device.mqtt_topic = topic
                device.lastseen_at = received_at                

                dbsession.commit()

            
            # process measurements
            if payloads and device: 

                # iterate all dictioniaries in payloads list
                for register in payloads:
                    
                    # type filter are values from register
                    if register["type"] == "filter":
                        
                        register_id = register["register"]["filterId"]
                        unit = register["register"]["unit"]
                        active = register["register"]["filterActive"]
                        measurement = None

                        # iterate all values from register
                        for index in reversed(range(len(register["register"]["values"]))):
                            
                            value = register["register"]["values"][index]
                            if value["valid"]:
                                status = 1
                            else:
                                status = 2

                            # check if THIS measurement already exists
                            measurement = dbsession.query(Measurement).filter_by(device_id=device.device_id,  received_at = received_at, register_id = register_id, measurement_nr = index).first()
                            if not measurement:
                                measurement = Measurement(
                                    device_id = device.device_id,
                                    received_at = received_at,
                                    register_id = register_id,
                                    measurement_nr = index,

                                    value = value["value"],
                                    unit = unit,
                                    status = status
                                )
                                dbsession.add(measurement)
                                dbsession.commit()

                            # fill loadprofile
                            # check out lastload
                            lastload = dbsession.query(Loadprofile).filter_by(device_id=device.device_id, register_id = register_id).order_by(Loadprofile.start_at.desc()).first()
                            if not lastload:
                                lastload = Loadprofile(
                                    device_id = device.device_id,
                                    register_id = register_id,
                                    start_at = received_at + timedelta(minutes=-15*index),
                                    load = 0,
                                    meterreading = value["value"],
                                    unit = unit,
                                    status = status
                                )
                                dbsession.add(lastload)
                                dbsession.commit()

                            # Checking difference
                            if measurement.value > lastload.meterreading:
                                lastload = Loadprofile(
                                    device_id = device.device_id,
                                    register_id = register_id,
                                    start_at = received_at + timedelta(minutes=-15*index),
                                    load = measurement.value - lastload.meterreading,
                                    meterreading = measurement.value,
                                    unit = unit,
                                    status = status
                                )
                                dbsession.add(lastload)
                                dbsession.commit()                                

                        # put last measurement in device
                        if measurement:

                            if register_id == 0:
                                device.register0_Active = active
                                device.register0_value = measurement.value
                                device.register0_unit = unit
                                device.register0_status = measurement.status 

                            elif register_id == 1:
                                device.register1_Active = active
                                device.register1_value = measurement.value
                                device.register1_unit = unit
                                device.register1_status = measurement.status                                                                              

                            elif register_id == 2:
                                device.register2_Active = active
                                device.register2_value = measurement.value
                                device.register2_unit = unit
                                device.register2_status = measurement.status     

                            elif register_id == 3:
                                device.register3_Active = active
                                device.register3_value = measurement.value
                                device.register3_unit = unit
                                device.register3_status = measurement.status                                            

                            dbsession.commit()


        # close dbsession
        dbsession.close_all()
    
    return
