"""
    imports & globals
"""

import datetime
import os

""" helpers """
# pylint: disable=E1101
def safe_cast(val, to_type, default=None, dformat=''):
    try:
        result = default
        if to_type in [datetime.datetime, datetime.date]:
            if type(val) == to_type:
                val = val.strftime(dformat)

            result = to_type.strptime(val, dformat)

        elif to_type is bool:
            result = str(val).lower() in ("yes", "true", "t", "1")

        elif to_type is str:
            if (isinstance(val, datetime.datetime) or isinstance(val, datetime.date)):
                result = str(val).strftime(dformat)
            else:
                result = str(val)
        else:
            result = to_type(val)

        return result

    except (ValueError, TypeError):
        return default


class AppConfiguration(object):
    """ configuraton class """

    _image = {}
    _dateformat = '%d.%m.%Y'
    _datetimeformat = '%d.%m.%Y %H:%M:%S'

    MYSQL_DB_NAME = 'smartenv'
    MYSQL_ROOT_PASSWORD = 'nosecrets'
    MYSQL_HOST = ''
    MYSQL_DATABASE_URI = ''
    MYSQL_DATABASE_BASE_URI = ''
    SQLALCHEMY_POOL_RECYCLE = 500

    LOG_LEVEL = 10
    APPLICATION_LOG_PATH = ''
    LOG_FILE = 'worker.log'

    SCHEDULE_MERGE_DEVICES = 60
    SCHEDULE_PULL_READINGS = 1
    # SCHEDULE_CLASSIFY_READINGS = 30

    DEMO_MODE = True

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
        self.LOG_FILE = os.path.join(self.APPLICATION_LOG_PATH, self.LOG_FILE)

        if self.MYSQL_HOST != '' and self.MYSQL_HOST:
            self.MYSQL_DATABASE_BASE_URI = 'mysql+pymysql://{0}:{1}@{2}'.format('root', self.MYSQL_ROOT_PASSWORD, self.MYSQL_HOST)
            self.MYSQL_DATABASE_URI = 'mysql+pymysql://{0}:{1}@{2}/{3}'.format('root', self.MYSQL_ROOT_PASSWORD, self.MYSQL_HOST, self.MYSQL_DB_NAME)

        else:
            self.MYSQL_DATABASE_BASE_URI = 'sqlite:///{0}'.format(self.APPLICATION_LOG_PATH)
            self.MYSQL_DATABASE_URI = 'sqlite:///{0}{1}'.format(self.APPLICATION_LOG_PATH, self.MYSQL_DB_NAME)

        """ parse self into dictionary """

        for key, value in vars(self).items():
            if not key.startswith('_') and key != '':
                self._image[key] = value

    def __repr__(self):
        """ return config members to dictionary """
        return str(self._image)
