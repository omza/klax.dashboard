from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from enum import Enum, unique
from hashlib import md5

from app.logic import utc2local_str

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

# Users
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

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
class Device(db.Model):
    __tablename__ = 'devices'

    device_id = db.Column(db.Integer, primary_key=True)
    device_extern_id = db.Column(db.String(40), nullable=False)
    inserted_at = db.Column(db.DateTime)  #: 2019-08-13T08:49:19.096588Z

    location_longitude = db.Column(db.Float)
    location_latitude = db.Column(db.Float)
    location_display_name = db.Column(db.String(255))
    comment = db.Column(db.String(255))

    dev_eui = db.Column(db.String(40), nullable=False)
    batteryPerc = db.Column(db.Integer, nullable=False) #100,
    configured = db.Column(db.Boolean) # true,
    connTest =   db.Column(db.Boolean) # false,
    deviceType = db.Column(db.String(255)) # "SML Klax",
    meterType = db.Column(db.String(255)) # "SML",
    version = db.Column(db.Integer, nullable=False) #1
    mqtt_topic = db.Column(db.String(255))

    register0_name = db.Column(db.String(50))
    register0_Active = db.Column(db.Boolean)
    register0_value = db.Column(db.Float, default=0.0)
    register0_unit = db.Column(db.String(5))
    register0_status = db.Column(db.Integer)    

    register1_name = db.Column(db.String(50))
    register1_Active = db.Column(db.Boolean)
    register1_value = db.Column(db.Float, default=0.0)
    register1_unit = db.Column(db.String(5))
    register1_status = db.Column(db.Integer)

    register2_name = db.Column(db.String(50))
    register2_Active = db.Column(db.Boolean)      
    register2_value = db.Column(db.Float, default=0.0)
    register2_unit = db.Column(db.String(5))
    register2_status = db.Column(db.Integer)    

    register3_name = db.Column(db.String(50))
    register3_Active = db.Column(db.Boolean)
    register3_value = db.Column(db.Float, default=0.0)
    register3_unit = db.Column(db.String(5))
    register3_status = db.Column(db.Integer)    

    lastseen_at = db.Column(db.DateTime)  #: 2019-08-13T08:49:19.096588Z

# Readings
class Measurement(db.Model):
    __tablename__ = 'measurements'

    device_id = db.Column(db.Integer, db.ForeignKey("devices.device_id"), primary_key=True, autoincrement=False)
    received_at = db.Column(db.DateTime, primary_key=True, autoincrement=False)  # 2019-06-24T20:48:09.167897Z,    
    register_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    measurement_nr  = db.Column(db.Integer, primary_key=True, autoincrement=False)

    value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(5))
    status = db.Column(db.Integer, nullable=False)
