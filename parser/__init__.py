from datetime import datetime, timezone
from sqlalchemy.orm import Session
from config import config
from parser.ttn import ttn_klax_parser
from enum import Enum, unique
from datetime import datetime
from dateutil import tz
import time

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

@unique
class ReadingStatus(Enum):
    valid = 1
    estimated = 2

def get_daytype(day):
    """
        determine a DayType depending on Speedfreak Calendar and the Day given
    """

    # determine season
    md = day.month * 100 + day.day

    if ((md > 320) and (md < 621)):
        daytype = 20  # spring
    elif ((md > 620) and (md < 923)):
        daytype = 10  # summer
    elif ((md > 922) and (md < 1223)):
        daytype = 20  # fall
    else:
        daytype = 30  # winter

    # determine weekdays
    if 0 <= day.weekday() <= 4:
        daytype = daytype + 1

    elif day.weekday() == 5:
        daytype = daytype + 2

    else:
        daytype = daytype + 3

    return DayType(daytype)

def message_distributor(topic: str, payload: str):
    """
        distribute message to fitting network parser
        and process to database

    """
    
    # extract topic and Payload from Message an distribute it
    if config.MQTT_SERVICE.upper() == 'TTN':
        ttn_klax_parser(topic, payload)


