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


def _root_path() -> Path:
    plugin_root = Path(__file__).parent.parent.parent
    if Path('/.dockerenv').exists():
        return plugin_root / 'aps' / 'api' / 'pydist'
    return plugin_root


def output_version_information(func):
    plugin_root = _root_path()
    if plugin_root.name != "pydist":
        raise FileNotFoundError(f"Can not find plugin root 'pydist'. Found {plugin_root.name}")

    def get_content(file_name: str) -> str:
        try:
            with open(plugin_root.parent / file_name) as f:
                return f.read().strip()
        except (FileNotFoundError, NotADirectoryError):
            plugin_file = str(plugin_root.parent.parent.absolute())
            try:
                archive = ZipFile(plugin_file, 'r')
                return archive.read(f'aps_gui/{file_name}').decode().strip()
            except:
                raise FileNotFoundError(f"Can not unzip and read plugin file with path {plugin_file}")
            finally:
                archive.close()

    @wraps(func)
    def decorator(config):

        if config.debug_level >= Debug.VERBOSE:
            print(f'Plugin running from: {plugin_root.parent}')

        version = get_content('VERSION')
        try:
            toolbox_version = get_content('STUB_VERSION')
        except:
            toolbox_version = ' '
        print(f"GUI version: {version}")

        if config.debug_level >= Debug.VERBOSE:
            print(f"APS toolbox (help script) version: {toolbox_version}  ")
            commit = get_content('COMMIT')
            print(f"Commit SHA: {commit}")
        return func(config)
    return decorator
