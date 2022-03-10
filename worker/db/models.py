# imports & globals
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum, unique


@unique
class HttpStatusCode(Enum):

    """ Http Status Code Enum.

    Example usage:
        HttpStatusCode.OK.value  # 100
        HttpStatusCode.INTERNAL_SERVER_ERROR.value  # 500
    """

    # INFORMATIONAL RESPONSES (100–199)
    CONTINUE = 100
    SWITCHING_PROTOCOL = 101
    PROCESSING = 102
    EARLY_HINTS = 103

    # SUCCESSFUL RESPONSES (200–299)
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226

    # REDIRECTS (300–399)
    MULTIPLE_CHOICE = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    UNUSED = 306
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308

    # CLIENT ERRORS (400–499)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    IM_A_TEAPOT = 418
    MISDIRECTED_REQUEST = 421
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    TOO_EARLY = 425
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    UNAVAILABLE_FOR_LEGAL_REASONS = 451

    # SERVER ERRORS (500–599)
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511

@unique
class ConnectorType(Enum):
    """ Types of possible Speedomat connectors

    Example usage:
        ConnectorType.ELEMENTIOT.value  # 1
    """
    ELEMENTIOT = 1
    TTN = 2

@unique
class Direction(Enum):
    """ Types of possible direction for measurements

    Example usage:
        Direction.LEAVE.value  # 1
    """
    LEAVE = 1
    APPROACH = 2

@unique
class SpeedingStatus(Enum):
    """ Types of possible Status for speedings

    Example usage:
        SpeedingStatus.GOOD.value  # 0
    """
    DEADSLOW = -2  # Red
    SLOW = -1  # Blue
    GOOD = 0  # Green
    WARNING = 1  # Yellow
    ALARM = 2  # Red

@unique
class DayType(Enum):
    """
        Classifies a Day into Cluster for prediction and comparison
        Example usage:
            DayType.SummerWeekday.value  # 11
    """
    SummerWeekday = 11
    SummerSaturday = 12
    SummerSunday = 13
    OtherSeasonWeekday = 21
    OtherSeasonSaturday = 22
    OtherSeasonSunday = 23
    WinterWeekday = 31
    WinterSaturday = 32
    WinterSunday = 33

# Models
Base = declarative_base()

# Users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    lastname = Column(String(80), unique=True, nullable=False)
    firstname = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    admin = Column(Boolean, default=False)


# Connectors
class Connector(Base):
    __tablename__ = 'connectors'

    connector_id = Column(Integer, primary_key=True)
    connector_type = Column(Integer, nullable=False)
    connector_database = Column(String(255), nullable=False)

# Devices
# {'temp': 17.6, 'so2': 0.0, 'pres': 983.1, 'power': 92, 'pm25': 6.31, 'pm10': 8.05, 'pm1': 5.45, 'o3': 0.0, 'no2': 0.0, 'hum': 74.2, 'co': 1.391}
class Devices(Base):
    __tablename__ = 'devices'

    device_id = Column(Integer, primary_key=True)
    connector_id = Column(Integer, ForeignKey("connectors.connector_id"), nullable=False)
    device_extern_id = Column(String(40), nullable=False)
    name = Column(String(255))  # Speed-o-mat Martinfeld,
    inserted_at = Column(DateTime)  #: 2019-08-13T08:49:19.096588Z
    location_longitude = Column(Float)
    location_latitude = Column(Float)
    location_display_name = Column(String(255))
    active = Column(Boolean, default=False)
    comment = Column(String(255))
    online_ticks_per_hour = Column(Integer, nullable=False)
    online_ticks = Column(Integer, nullable=False)
    first_tick_at = Column(DateTime)
    last_tick_at = Column(DateTime)
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
class Speedfreak(Base):
    __tablename__ = 'speedfreaks'

    speedfreak_id = Column(Integer, primary_key=True)
    connector_id = Column(Integer, ForeignKey("connectors.connector_id"), nullable=False)
    speedfreak_extern_id = Column(String(40), nullable=False)
    name = Column(String(255))  # Speed-o-mat Martinfeld,
    inserted_at = Column(DateTime)  #: 2019-08-13T08:49:19.096588Z
    location_longitude = Column(Float)
    location_latitude = Column(Float)
    location_display_name = Column(String(255))
    speedlimit = Column(Integer, default=0)
    active = Column(Boolean, default=False)
    comment = Column(String(255))
    online_ticks_per_hour = Column(Integer, nullable=False)
    online_ticks = Column(Integer, nullable=False)
    first_tick_at = Column(DateTime)
    last_tick_at = Column(DateTime)
    cars_total = Column(Integer, nullable=False)
    cars_small = Column(Integer, nullable=False)
    cars_medium = Column(Integer, nullable=False)
    cars_large = Column(Integer, nullable=False)
    cars_huge = Column(Integer, nullable=False)
    cars_aproaching = Column(Integer, nullable=False)
    cars_leaving = Column(Integer, nullable=False)
    speed_alarms = Column(Integer, nullable=False)
    speed_warnings = Column(Integer, nullable=False)
    speed_deadslows = Column(Integer, nullable=False)
    speed_normals = Column(Integer, nullable=False)
    speed_min = Column(Float, nullable=False)
    speed_max = Column(Float, nullable=False)
    speed_avg = Column(Float, nullable=False)
    rebuild_until_measurement_id = Column(Integer, default=0)
    speed_alarm_threshold = Column(Integer)
    speed_alarm_label = Column(String(20))
    speed_warning_threshold = Column(Integer)
    speed_warning_label = Column(String(20))
    chart_color_code = Column(String(25))
"""

# Readings
class Measurement(Base):
    __tablename__ = 'measurements'

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.device_id"), primary_key=True, autoincrement=False)
    measurement_extern_id = Column(String(40), nullable=False)  # a28000d6-18c7-4099-9bb7-976a3ece92cc,
    device_extern_id = Column(String(40), nullable=False)  # d3829df3-cb83-4691-aae8-9cf70ed85863,
    measured_at = Column(DateTime)  # 2019-06-24T20:48:09.167897Z,
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
class Measurement(Base):
    __tablename__ = 'measurements'

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    speedfreak_id = Column(Integer, ForeignKey("speedfreaks.speedfreak_id"), primary_key=True, autoincrement=False)
    measurement_extern_id = Column(String(40), nullable=False)  # a28000d6-18c7-4099-9bb7-976a3ece92cc,
    speedfreak_extern_id = Column(String(40), nullable=False)  # d3829df3-cb83-4691-aae8-9cf70ed85863,
    measured_at = Column(DateTime)  # 2019-06-24T20:48:09.167897Z,
    speed = Column(Float)
    direction = Column(Integer)
    speeding = Column(Float)
    speeding_status = Column(Integer)
"""
# Load Profile 1 datapoint every Hour
# Datetime in UTC
# {'type': 'summary', 'speed_min': 47, 'speed_max': 47, 'speed_avg': 47.0, 'measurements_total': 1, 'cars_small': 0, 'cars_medium': 0, 'cars_large': 0, 'cars_huge': 1}
# {'type': 'single_speed', 'speed': 36, 'direction': 'approaching'}
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

# Comparison 1 datapoint every 15 Minutes
# Datetime in UTC
# {'type': 'summary', 'speed_min': 47, 'speed_max': 47, 'speed_avg': 47.0, 'measurements_total': 1, 'cars_small': 0, 'cars_medium': 0, 'cars_large': 0, 'cars_huge': 1}
# {'type': 'single_speed', 'speed': 36, 'direction': 'approaching'}
"""
class DayTypeTimeSeries(Base):
    __tablename__ = 'daytype_timeseries'

    daytype_id = Column(Integer, primary_key=True, autoincrement=False)
    speedfreak_id = Column(Integer, ForeignKey("speedfreaks.speedfreak_id"), primary_key=True, autoincrement=False)
    time_from = Column(DateTime, primary_key=True, autoincrement=False)
    time_to = Column(DateTime, nullable=False)
    cars_total = Column(Integer, nullable=False)
    cars_small = Column(Integer, nullable=False)
    cars_medium = Column(Integer, nullable=False)
    cars_large = Column(Integer, nullable=False)
    cars_huge = Column(Integer, nullable=False)
    cars_aproaching = Column(Integer, nullable=False)
    cars_leaving = Column(Integer, nullable=False)
    speed_alarms = Column(Integer, nullable=False)
    speed_deadslows = Column(Integer, nullable=False)
    speed_normals = Column(Integer, nullable=False)
    speed_min = Column(Float, nullable=False)
    speed_max = Column(Float, nullable=False)
    speed_avg = Column(Float, nullable=False)
"""