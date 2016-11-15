from functools import wraps
from urllib.parse import unquote


def decode_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*[unquote(arg) for arg in args], **kwargs)
    return wrapper
