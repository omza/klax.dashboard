from datetime import datetime, date, timezone
import time
import pytz

def safe_cast(val, to_type, default=None, dformat=''):
    try:
        result = default
        if to_type in [datetime, datetime.date]:
            if type(val) == to_type:
                val = val.strftime(dformat)

            result = to_type.strptime(val, dformat)

        elif to_type is bool:
            result = str(val).lower() in ("yes", "true", "t", "1")

        elif to_type is str:
            if (isinstance(val, datetime) or isinstance(val, date)):
                result = str(val.strftime(dformat))
            else:
                result = str(val)
        else:
            result = to_type(val)

        return result

    except (ValueError, TypeError):
        return default

def utc2local(utc, timezone: str) -> datetime:
    offset = pytz.timezone(timezone).localize(utc).utcoffset()
    local = utc + offset
    return local

def local2utc(local, timezone: str) -> datetime:
    local = pytz.timezone(timezone).localize(local)
    utc = local.astimezone(pytz.utc)
    return utc    