from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from enum import Enum, unique
from hashlib import md5

from app.logic import utc2local_str

# silly user model
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    lastname = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"id: {self.id}, lastname: {self.lastname}, email: {self.email}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

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
        SpeedingStatus.LEAVE.value  # 1
    """
    DEADSLOW = -1  # Blue
    GOOD = 0  # Green
    WARNING = 1  # Yellow
    ALARM = 2  # Red

# Connectors
class Connector(db.Model):
    __tablename__ = 'connectors'

    connector_id = db.Column(db.Integer, primary_key=True)
    connector_type = db.Column(db.Integer, nullable=False)
    connector_database = db.Column(db.String(255), nullable=False)

# Devices
"""
class Speedfreak(db.Model):
    __tablename__ = 'speedfreaks'

    speedfreak_id = db.Column(db.Integer, primary_key=True)
    connector_id = db.Column(db.Integer, nullable=False)
    speedfreak_extern_id = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(255))  # Speed-o-mat Martinfeld,
    inserted_at = db.Column(db.DateTime)  #: 2019-08-13T08:49:19.096588Z
    location_longitude = db.Column(db.Float)
    location_latitude = db.Column(db.Float)
    location_display_name = db.Column(db.String(255))
    speedlimit = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(255))
    online_ticks_per_hour = db.Column(db.Integer, nullable=False)
    online_ticks = db.Column(db.Integer, nullable=False)
    first_tick_at = db.Column(db.DateTime)
    last_tick_at = db.Column(db.DateTime)
    cars_total = db.Column(db.Integer, nullable=False)
    cars_small = db.Column(db.Integer, nullable=False)
    cars_medium = db.Column(db.Integer, nullable=False)
    cars_large = db.Column(db.Integer, nullable=False)
    cars_huge = db.Column(db.Integer, nullable=False)
    cars_aproaching = db.Column(db.Integer, nullable=False)
    cars_leaving = db.Column(db.Integer, nullable=False)
    speed_alarms = db.Column(db.Integer, nullable=False)
    speed_warnings = db.Column(db.Integer, nullable=False)
    speed_deadslows = db.Column(db.Integer, nullable=False)
    speed_normals = db.Column(db.Integer, nullable=False)
    speed_min = db.Column(db.Float, nullable=False)
    speed_max = db.Column(db.Float, nullable=False)
    speed_avg = db.Column(db.Float, nullable=False)
    rebuild_until_measurement_id = db.Column(db.Integer, default=0)
    speed_alarm_threshold = db.Column(db.Integer)
    speed_alarm_label = db.Column(db.String(20))
    speed_warning_threshold = db.Column(db.Integer)
    speed_warning_label = db.Column(db.String(20))
    chart_color_code = db.Column(db.String(25))

    measurements = db.relationship('Measurement')
    datapoints = db.relationship('CarTimeSeries')

    def connector(self):
        return ConnectorType(self.connector_id).name

    def local_inserted_at(self):
        return utc2local_str(self.inserted_at)

    def local_last_tick_at(self):
        return utc2local_str(self.last_tick_at)
"""
class Devices(db.Model):
    __tablename__ = 'devices'

    device_id = db.Column(db.Integer, primary_key=True)
    connector_id = db.Column(db.Integer, db.ForeignKey("connectors.connector_id"), nullable=False)
    device_extern_id = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(255))  # Speed-o-mat Martinfeld,
    inserted_at = db.Column(db.DateTime)  #: 2019-08-13T08:49:19.096588Z
    location_longitude = db.Column(db.Float)
    location_latitude = db.Column(db.Float)
    location_display_name = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(255))
    online_ticks_per_hour = db.Column(db.Integer, nullable=False)
    online_ticks = db.Column(db.Integer, nullable=False)
    first_tick_at = db.Column(db.DateTime)
    last_tick_at = db.Column(db.DateTime)
    temp = db.Column(db.Float, default=0.0)
    so2 = db.Column(db.Float, default=0.0)
    pres = db.Column(db.Float, default=0.0)
    power = db.Column(db.Float, default=0.0)
    pm25 = db.Column(db.Float, default=0.0)
    pm10 = db.Column(db.Float, default=0.0)
    pm1 = db.Column(db.Float, default=0.0)
    o3 = db.Column(db.Float, default=0.0)
    no2 = db.Column(db.Float, default=0.0)
    hum = db.Column(db.Float, default=0.0)
    co = db.Column(db.Float, default=0.0)

    measurements = db.relationship('Measurement')
    datapoints = db.relationship('TimeSeries')

    def connector(self):
        return ConnectorType(self.connector_id).name

    def local_inserted_at(self):
        return utc2local_str(self.inserted_at)

    def local_last_tick_at(self):
        return utc2local_str(self.last_tick_at)

# Readings
class Measurement(db.Model):
    __tablename__ = 'measurements'

    measurement_id = db.Column(db.String(40), primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'), primary_key=True)
    measurement_extern_id = db.Column(db.String(40), nullable=False)  # a28000d6-18c7-4099-9bb7-976a3ece92cc,
    device_extern_id = db.Column(db.String(40), nullable=False)  # d3829df3-cb83-4691-aae8-9cf70ed85863,
    measured_at = db.Column(db.DateTime)  # 2019-06-24T20:48:09.167897Z,
    temp = db.Column(db.Float, default=0.0)
    so2 = db.Column(db.Float, default=0.0)
    pres = db.Column(db.Float, default=0.0)
    power = db.Column(db.Float, default=0.0)
    pm25 = db.Column(db.Float, default=0.0)
    pm10 = db.Column(db.Float, default=0.0)
    pm1 = db.Column(db.Float, default=0.0)
    o3 = db.Column(db.Float, default=0.0)
    no2 = db.Column(db.Float, default=0.0)
    hum = db.Column(db.Float, default=0.0)
    co = db.Column(db.Float, default=0.0)

# Load Profile 1 datapoint every 15 Minutes
# Datetime in UTC
class TimeSeries(db.Model):
    __tablename__ = 'timeseries'

    device_id = db.Column(db.Integer, db.ForeignKey("devices.device_id"), primary_key=True, autoincrement=False)
    datetime_from = db.Column(db.DateTime, primary_key=True, autoincrement=False)
    datetime_to = db.Column(db.DateTime, nullable=False)
    daytype_id = db.Column(db.Integer, nullable=False)
    online_ticks = db.Column(db.Integer, nullable=False)
    temp = db.Column(db.Float, default=0.0)
    so2 = db.Column(db.Float, default=0.0)
    pres = db.Column(db.Float, default=0.0)
    power = db.Column(db.Float, default=0.0)
    pm25 = db.Column(db.Float, default=0.0)
    pm10 = db.Column(db.Float, default=0.0)
    pm1 = db.Column(db.Float, default=0.0)
    o3 = db.Column(db.Float, default=0.0)
    no2 = db.Column(db.Float, default=0.0)
    hum = db.Column(db.Float, default=0.0)
    co = db.Column(db.Float, default=0.0)
