import json
import random
import string
import time
from base64 import b64decode
from functools import wraps

from src.utils.constants.simple import Debug


def cached(func):
    @wraps(func)
    def wrapper(self):
        name = '_' + func.__name__
        if not hasattr(self, name):
            result = func(self)
            setattr(self, name, result)
        return getattr(self, name)

    return wrapper


def loggable(func):
    @wraps(func)
    def wrapper(config):
        if config['errorMessage']:
            return func(config)
        try:
            return func(config)
        except Exception as e:
            if config['parameters']['debugLevel']['selected'] >= Debug.ON:
                print('The workflow failed. The job and the model will be written to disk')
                when = time.localtime()
                prefix = '{year}{month:02}{day:02}-{hour:02}{minute:02}{second:02}-{random}-APS'.format(
                    year=when.tm_year,
                    month=when.tm_mon,
                    day=when.tm_mday,
                    hour=when.tm_hour,
                    minute=when.tm_min,
                    second=when.tm_sec,
                    random=''.join(random.choices(string.ascii_letters + string.digits, k=5)),
                )
                model = config['model']
                with open(prefix + '.model.xml', 'wb') as f:
                    f.write(b64decode(model))
                with open(prefix + '.state.json', 'w') as f:
                    json.dump(config, f)
            raise e

    return wrapper
