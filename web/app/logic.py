# datetime convert
import pytz
from datetime import datetime, date
import time
# import random

local_tz = pytz.timezone('Europe/Berlin')

def utc2local(utc_dt):

    if isinstance(utc_dt, datetime):
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)  # .normalize might be unnecessary

    else:
        return None

def utcdate2local(utc_d):
    if isinstance(utc_d, date):
        utc_dt = datetime(
            year=utc_d.year,
            month=utc_d.month,
            day=utc_d.day,
        )
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)  # .normalize might be unnecessary
    else:
        return None

def utc2local_str(utc_dt):
    local_dt = utc2local(utc_dt)
    if isinstance(local_dt, datetime):
        return local_dt.strftime('%d.%m.%Y %H:%M:%S')
    else:
        return ''

def utc2local_date_str(utc_dt):
    local_dt = utcdate2local(utc_dt)
    if isinstance(local_dt, datetime) or isinstance(local_dt, date):
        return local_dt.strftime('%d.%m.%Y')
    else:
        return ''

# Random Colors
COLORS_RGBA = [(139, 0, 0, 0.4), (0, 100, 0, 0.4), (0, 0, 139, 0.4), (255, 0, 0, 0.4), (0, 255, 0, 0.4), (0, 0, 255, 0.4)]
def random_color_rgba():
    return random.choice(COLORS_RGBA)


def number_format(x, country='de_DE'):
    """ Format a given number (integer or float) to locale setting """
    if isinstance(x, int):
        return '{:,}'.format(x).replace(",", "X").replace(".", ",").replace("X", ".")

    elif isinstance(x, float):
        x = round(x, 2)
        return '{:,}'.format(x).replace(",", "X").replace(".", ",").replace("X", ".")

    else:
        return str(x)
