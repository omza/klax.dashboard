"""
    imports & globals
"""

import datetime
import os
from tools.convert import safe_cast


class AppConfiguration(object):
    """ configuraton class """

    _image = {}

    #
    #  Application Settings
    #
    PATH_LOG = ''
    DOCKER_PATH_LOG = ""
    LOG_FILE = "klax.log"
    LOG_LEVEL = 10 #debug
    TIMEZONE = "Europe/Berlin"

    #
    # The Klax Device
    #
    END_DEVICE_ID = 'klax_demo'

    #
    # SQLLITE Database Configuration
    #
    DB_NAME = 'klaxdb'
    DATABASE_URI = ""

    #
    # Web User
    #
    USER_FIRSTNAME = ''
    USER_EMAIL = ''
    USER_PASS = '' 

    #
    # Configure MQTT Service
    #
    MQTT_HOST=''
    MQTT_PORT=8883
    MQTT_USER=''
    MQTT_PASSWORD=''
    MQTT_TOPIC='#'
    MQTT_SERVICE='TTN'

    #
    # Configure Datetime formats
    #
    DATEFORMAT = '%d.%m.%Y'
    DATETIMEFORMAT = '%d.%m.%Y %H:%M:%S'

    #
    # fastapi-login configuration
    #
    SECRET = 'super-secret-key'

    def __init__(self):
        """ constructor """

        for key, default in vars(self.__class__).items():
            if not key.startswith('_') and key != '':
                if key in os.environ.keys():

                    value = os.environ.get(key)
                    to_type = type(default)

                    if to_type is datetime.datetime:
                        setattr(self, key, safe_cast(value, to_type, default, self._datetimeformat))

                    elif to_type is datetime.date:
                        setattr(self, key, safe_cast(value, to_type, default, self._dateformat))

                    else:
                        setattr(self, key, safe_cast(value, to_type, default))
                else:
                    setattr(self, key, default)

        # Custom Configuration part
        if self.DOCKER_PATH_LOG != "":
            self.PATH_LOG = self.DOCKER_PATH_LOG

        self.LOG_FILE = os.path.join(self.PATH_LOG, self.LOG_FILE)
        self.DATABASE_URI = 'sqlite:///{0}'.format(os.path.join(self.PATH_LOG, self.DB_NAME))
        
        """ parse self into dictionary """



        for key, value in vars(self).items():
            if not key.startswith('_') and key != '':
                self._image[key] = value

    def __repr__(self):
        """ return config members to dictionary """
        return str(self._image)
