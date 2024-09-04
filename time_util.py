# time_util.py

import datetime
import pytz

def get_current_time(timezone='Asia/Kolkata'):
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)
    return now.strftime('%Y-%m-%d %H:%M:%S %Z%z')

def get_timezone_name(timezone='Asia/Kolkata'):
    tz = pytz.timezone(timezone)
    return tz.zone
