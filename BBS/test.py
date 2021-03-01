
from functools import wraps

def outer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
