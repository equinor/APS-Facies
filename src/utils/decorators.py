from functools import wraps


def cached(func):
    @wraps(func)
    def wrapper(self):
        name = '_' + func.__name__
        if not hasattr(self, name):
            result = func(self)
            setattr(self, name, result)
        return getattr(self, name)
    return wrapper
