# -*- coding: utf-8 -*-
from typing import Optional, List
from warnings import warn


def running_in_batch_mode():
    try:
        import roxar.rms
    except ImportError:
        return False
    return roxar.rms.get_execution_mode() == roxar.ExecutionMode.Batch


def must_run_in_rms(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import roxar.rms
            try:
                if roxar.__mock__:
                    warn(f'{func.__name__} must be run in RMS, but the usage of a mock was detected.')
                    return None
            except AttributeError:
                # This should mean, that we are running inside RMS
                return func(*args, **kwargs)
        except ImportError:
            warn(f'{func.__name__} must be run in RMS, but no \'roxar\' module was found.')
            return None

        return func(*args, **kwargs)
    return wrapper


@must_run_in_rms
def get_nrlib_path():
    import platform

    description = platform.platform()
    if 'redhat' in description:
        # Assuming we are on RGS
        redhat_version = get_redhat_version()
        rms_version = get_rms_version()[0]
        return f'/project/res/nrlib/nrlib-dist-RHEL{redhat_version}-RMS{rms_version}'


def get_rms_version():
    try:
        import roxar.rms
    except ImportError:
        return None

    rms_version = roxar.rms.get_version().split('.')
    if len(rms_version) == 2:
        rms_version.append('0')
    return rms_version


def get_redhat_version():
    import re
    import platform

    description = platform.platform()
    return re.match(r'.*redhat-(?P<major>[0-9]+).*', description).groupdict()['major']


@must_run_in_rms
def get_rgs_specific_python_package_paths() -> Optional[List[str]]:
    import sys

    python_version = sys.version_info
    python_version = f'{python_version.major}.{python_version.minor}'

    common_equinor_path = (
        '/project/res/roxapi/x86_64_RH_{redhat_version}/{rms_version}/lib/python{python_version}/site-packages'
        ''.format(
            redhat_version=get_redhat_version(),
            rms_version='.'.join(get_rms_version()),
            python_version=python_version,
        )
    )

    return [common_equinor_path]


def get_common_python_packages_paths() -> List[str]:
    import sys

    rgs_paths = get_rgs_specific_python_package_paths() or []

    return rgs_paths + [path for path in sys.path if path.endswith('site-packages')]


def import_module(name: str, dependencies: Optional[List[str]] = None, min_version: Optional[str] = None) -> None:
    from src.utils.roxar import get_common_python_packages_paths
    paths = get_common_python_packages_paths()

    import sys
    import importlib.util
    from pathlib import Path
    if dependencies is None:
        dependencies = []

    for name in [*reversed(dependencies), name]:
        try:
            del sys.modules[name]
        except KeyError:
            pass

        imported = False
        for path in paths:
            package_path = Path(f'{path}/{name}/__init__.py')
            if not imported and package_path.exists():
                spec = importlib.util.spec_from_file_location(name, str(package_path))
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                imported = True
    if not imported:
        raise ModuleNotFoundError(f"No module named '{name}'")

    if min_version is not None:
        from packaging.version import parse
        module = sys.modules[name]
        try:
            module_version = module.__version__
            if parse(module_version) < parse(min_version):
                raise ImportError(
                    f"APS requires version {min_version}, or higher of '{name}', but {module_version} was installed."
                )
        except AttributeError:
            warn(
                f"APS requires {min_version}, or higher of '{name}', but not version information could be gathered.\n"
                f"This may be OK, but if you encounter errors related to '{name}', consider updating it."
            )
