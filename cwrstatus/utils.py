from datetime import datetime
import uuid


def get_current_utc_time():
    return datetime.utcnow().isoformat()


def generate_test_id():
    return uuid.uuid4().hex
