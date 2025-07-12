_timer_cancelled = False

def get_timer_cancelled():
    return _timer_cancelled

def set_timer_cancelled(value):
    global _timer_cancelled
    _timer_cancelled = value
