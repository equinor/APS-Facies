# Set path to the aps code unpacked from the plugin file

import roxar.rms

from zipfile import ZipFile
from importlib import import_module
from pathlib import Path
from functools import wraps
import os
import sys
import shutil


# Define all used environment variables
APS_ROOT                  = 'APS_ROOT'
RMS_PLUGINS_LIBRARY       = 'RMS_PLUGINS_LIBRARY'

# Path to where the file below is located within the repository
relative_path = 'aps/toolbox'


def unpack_aps_code_and_load_module(module_name):
    temp_dir = Path(roxar.rms.get_tmp_dir())
    root_path = _get_path_from_environment(APS_ROOT, temp_dir / 'aps_gui' / 'pydist')
    if APS_ROOT not in os.environ:
        # Add the path to searchable path
        # Assumed that the plugin should not be used, if 'APS_ROOT' is set

        # When a plugin is used, it includes a stump for importing gaussianfft as well
        print(f"Unpack code to temporary directory: {root_path} ")
        _extract_plugin(temp_dir)
        sys.path.insert(0, _stringify_path(root_path))
    else:
        print(f"Use source code from: {root_path} ")

    module_path = relative_path.replace('/', '.') + '.' + module_name
    print(f"Load module: {module_path}\n")
    return import_module(module_path)


# Utils
def _get_path_from_environment(environment_name, default_name):
    paths = os.environ.get(environment_name, default_name)
    if isinstance(paths, str):
        return Path(paths.split(':')[0])
    return paths

def _get_plugin_dir():
    version = roxar.rms.get_version()
    try:
        major, minor, patch = version.split('.')
        if minor == '0':
            rms_version = major
        else:
            rms_version = major + '.' + minor
    except ValueError:
        rms_version = version
    preferences = Path(Path.home() / '.roxar/rms-{}/preferences.master'.format(rms_version))
    with open(preferences) as f:
        lines = f.readlines()
    
    plugin_dir = _get_path_from_environment(RMS_PLUGINS_LIBRARY, '/project/res/APSGUI/releases/stable')
    for line in lines:
        if line.startswith('jobplugindir'):
            new_location = line.split('=')[1].strip()
            if new_location:
                # The location may be set to an empty string
                plugin_dir = Path(new_location)
    return plugin_dir

def _get_current_plugin_path():
    # TODO: Get the version RMS is _actually_ using
    #       That is, RMS _could_ be using a different version than what is _should_ (this happens occasionally)
    paths = [p.absolute() for p in _get_plugin_dir().glob('aps_gui*')]
    version_data = []
    current_path = None
    #File format: directorypath/aps_gui.major.minor.patch.plugin   or
    #             directorypath/aps_gui.major.minor.patch.timestamp.plugin
    #Example /project/res/APSGUI/releases/aps_gui.1.3.10.221991918.plugin  or
    #        /project/res/APSGUI/releases/stable/aps_gui.1.3.10.plugin
    for path in paths:
        last_suffix = path.suffixes[-1]
        if last_suffix == '.plugin':
            suffixes = [int(suffix.strip('.')) for suffix in path.suffixes[:-1]]
            if len(suffixes) == 3:
                # That is, major, minor, patch
                suffixes.append(float('inf'))
            version_data.append((path, tuple(suffixes)))
    if version_data:
        # Sort on version numbering
        version_data.sort(key=lambda x: (x[-1]))
        current_path = version_data[-1][0]
    text = 'Plugin_path: ' + str(current_path)
    print(text)
    return current_path

def _stringify_path(path):
    return str(path.absolute())

def _extract_plugin(temp_dir):
    extracted = temp_dir / 'aps_gui'
    current_plugin_path = _get_current_plugin_path()
    def unzip():
        with ZipFile(str(current_plugin_path)) as zf:
            zf.extractall(path=temp_dir)
    if not extracted.exists():
        unzip()
    else:
        # Check that the version of the extracted plugin is the same as the expected version
        with open(extracted / 'VERSION') as f:
            for line in f.readlines():
                if line:
                    extracted_version = line.strip()
                    break
        if not current_plugin_path.match('*' + extracted_version + '*'):
            # A refresh is required
            shutil.rmtree(extracted, ignore_errors=True)
            unzip()
