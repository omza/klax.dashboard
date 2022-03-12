# imports & globals
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5


# Models
Base = declarative_base()

# Users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))

    def __str__(self):
        return f"id: {self.id}, firstname: {self.firstname}, email: {self.email}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


# Devices
class Device(Base):
    __tablename__ = 'devices'

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



# Load Profile 1 datapoint every Hour
# Datetime in UTC
# {'type': 'summary', 'speed_min': 47, 'speed_max': 47, 'speed_avg': 47.0, 'measurements_total': 1, 'cars_small': 0, 'cars_medium': 0, 'cars_large': 0, 'cars_huge': 1}
# {'type': 'single_speed', 'speed': 36, 'direction': 'approaching'}

"""
class TimeSeries(Base):
    __tablename__ = 'timeseries'

    device_id = Column(Integer, ForeignKey("devices.device_id"), primary_key=True, autoincrement=False)
    datetime_from = Column(DateTime, primary_key=True, autoincrement=False)
    datetime_to = Column(DateTime, nullable=False)
    daytype_id = Column(Integer, nullable=False)
    online_ticks = Column(Integer, nullable=False)
    temp = Column(Float, default=0.0)
    so2 = Column(Float, default=0.0)
    pres = Column(Float, default=0.0)
    power = Column(Float, default=0.0)
    pm25 = Column(Float, default=0.0)
    pm10 = Column(Float, default=0.0)
    pm1 = Column(Float, default=0.0)
    o3 = Column(Float, default=0.0)
    no2 = Column(Float, default=0.0)
    hum = Column(Float, default=0.0)
    co = Column(Float, default=0.0)
"""
