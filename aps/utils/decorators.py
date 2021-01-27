from functools import wraps
from pathlib import Path
from zipfile import ZipFile

from aps.utils.constants.simple import Debug
from aps.utils.debug import dump_debug_information


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
        if config.error_message:
            return func(config)
        try:
            return func(config)
        except Exception as e:
            dump_debug_information(config)
            raise e

    return wrapper


def output_version_information(func):
    plugin_root = Path(__file__).parent.parent.parent.parent

    def get_content(file_name: str) -> str:
        try:
            with open(plugin_root / file_name) as f:
                return f.read().strip()
        except (FileNotFoundError, NotADirectoryError):
            # This means that the plugin is running in RMS
            archive = ZipFile(str(plugin_root.parent.absolute()), 'r')
            try:
                return archive.read(f'aps_gui/{file_name}').decode().strip()
            finally:
                archive.close()

    @wraps(func)
    def decorator(config):

        if config.debug_level >= Debug.VERBOSE:
            print(f'Plugin running from: {plugin_root.parent}')

        version = get_content('VERSION')
        print(f"GUI version: {version}")
        if config.debug_level >= Debug.VERBOSE:
            commit = get_content('COMMIT')
            print(f"Commit SHA: {commit}")
        return func(config)
    return decorator
