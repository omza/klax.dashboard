# imports & globals
from contextlib import nullcontext
from inspect import Attribute
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from config import config

from datetime import datetime, timezone
import time 

from tools.convert import utc2local


# Models
Base = declarative_base()

# Users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    #cookies_check = Column(Boolean, default=False)

    def __str__(self):
        return f"id: {self.id}, firstname: {self.firstname}, email: {self.email}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(str(self.password_hash), password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_authenticated(self):
        return True

    def admin(self):
        return True

# Devices
class Device(Base):
    __tablename__ = 'devices'
    _ticks = 0

    device_id = Column(Integer, primary_key=True)
    device_extern_id = Column(String(40), nullable=False)
    inserted_at = Column(DateTime)  #: 2019-08-13T08:49:19.096588Z

    location_longitude = Column(Float)
    location_latitude = Column(Float)
    location_display_name = Column(String(255))
    comment = Column(String(255))

    dev_eui = Column(String(40), nullable=False)
    batteryPerc = Column(Integer, nullable=False) #100,
    configured = Column(Boolean) # true,
    connTest =   Column(Boolean) # false,
    deviceType = Column(String(255)) # "SML Klax",
    meterType = Column(String(255)) # "SML",
    version = Column(Integer, nullable=False) #1
    mqtt_topic = Column(String(255))

    register0_name = Column(String(50))
    register0_Active = Column(Boolean)
    register0_value = Column(Float, default=0.0)
    register0_unit = Column(String(5))
    register0_status = Column(Integer)    

    register1_name = Column(String(50))
    register1_Active = Column(Boolean)
    register1_value = Column(Float, default=0.0)
    register1_unit = Column(String(5))
    register1_status = Column(Integer)

    register2_name = Column(String(50))
    register2_Active = Column(Boolean)      
    register2_value = Column(Float, default=0.0)
    register2_unit = Column(String(5))
    register2_status = Column(Integer)    

    register3_name = Column(String(50))
    register3_Active = Column(Boolean)
    register3_value = Column(Float, default=0.0)
    register3_unit = Column(String(5))
    register3_status = Column(Integer)    

    lastseen_at = Column(DateTime)  #: 2019-08-13T08:49:19.096588Z

    def kWh(self, register_id) -> int:

        kwh: int = -1

        if 0 <= register_id <3:

            if register_id == 0:
                if self.register0_Active:
                    kwh = round(self.register0_value/1000,0)
                    
            elif register_id == 1:
               if self.register1_Active:
                    kwh = round(self.register1_value/1000,0)

            elif register_id == 2:
               if self.register2_Active:
                    kwh = round(self.register2_value/1000,0)

            elif register_id == 3:
               if self.register3_Active:
                    kwh = round(self.register3_value/1000,0)                   
        
        if kwh >= 0:
            return kwh
        else:
            return -1

    def created(self) -> str:
        result = self.inserted_at.strftime(config.DATETIMEFORMAT)
        return result

    def lastseen(self) -> str:
        result = utc2local(self.lastseen_at, config.TIMEZONE).strftime(config.DATETIMEFORMAT)
        return result
    
    def lorawan(self) -> dict:
        backend = {'name': '', 'link': ''}

        if config.MQTT_SERVICE == "TTN":
            backend['name'] = 'the things network'
            backend['link'] = 'https://www.thethingsnetwork.org/'
        
        return backend

    def availability(self) -> dict:
        
        duration = self.lastseen_at - self.inserted_at
        duration_in_s = duration.total_seconds()
        hours = divmod(duration_in_s, 3600)[0]

        percent = round(self._ticks/hours * 100, 0)

        if percent >= 90:
            label = 'success'
            if percent > 100:
                percent = 100
        elif percent > 50:
            label = 'warning'
        else:
            label = 'danger'

        overallavailability = {'percent': percent, 'label': label}

        return overallavailability    

    @property
    def ticks(self) -> int:
        return self._ticks

    @ticks.setter
    def ticks(self, value: int):
        self._ticks = value


# Readings
class Measurement(Base):
    __tablename__ = 'measurements'

    device_id = Column(Integer, ForeignKey("devices.device_id"), primary_key=True, autoincrement=False)
    received_at = Column(DateTime, primary_key=True, autoincrement=False)  # 2019-06-24T20:48:09.167897Z,    
    register_id = Column(Integer, primary_key=True, autoincrement=False)
    measurement_nr  = Column(Integer, primary_key=True, autoincrement=False)

    value = Column(Float, default=0.0)
    unit = Column(String(5))
    status = Column(Integer, nullable=False)


class Loadprofile(Base):
    __tablename__ = 'timeseries'

    device_id = Column(Integer, ForeignKey("devices.device_id"), primary_key=True, autoincrement=False)
    register_id = Column(Integer, primary_key=True, autoincrement=False)
    start_at = Column(DateTime, primary_key=True, autoincrement=False) 

    load = Column(Float)
    meterreading = Column(Float)
    unit = Column(String(5))
    status = Column(Integer, nullable=False)