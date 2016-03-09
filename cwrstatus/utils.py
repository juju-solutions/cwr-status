from datetime import datetime


def get_current_utc_time():
    return datetime.utcnow().isoformat()