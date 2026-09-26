import os
from datetime import datetime
from zoneinfo import ZoneInfo

def get_timezone() -> ZoneInfo:
    tz_name = os.getenv("TZ", "America/Sao_Paulo")
    return ZoneInfo(tz_name)

def get_now() -> datetime:
    return datetime.now(get_timezone())
