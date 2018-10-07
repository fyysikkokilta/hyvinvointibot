"""
Small utility functions.
"""

import time
from datetime import datetime

def is_today(unix_time_seconds):
    d = datetime.fromtimestamp(unix_time_seconds).date()
    today = datetime.now().date()
    return d == today

# tests
if __name__ == "__main__":
    assert is_today(time.time())
    assert not is_today(time.time() - 60 * 60 * 24)
