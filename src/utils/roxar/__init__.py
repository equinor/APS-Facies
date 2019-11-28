# -*- coding: utf-8 -*-
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
                    return None
            except AttributeError:
                pass
        except ImportError:
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
        return '/project/res/nrlib/nrlib-dist-RHEL{}-RMS{}'.format(redhat_version, rms_version)


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
    redhat_version = re.match(r'.*redhat-(?P<major>[0-9]+).*', description).groupdict()['major']
    return redhat_version


@must_run_in_rms
def get_common_python_packages_path():
    import sys

    python_version = sys.version_info
    python_version = '{}.{}'.format(python_version.major, python_version.minor)

    return (
        '/project/res/roxapi/x86_64_RH_{redhat_version}/{rms_version}/lib/python{python_version}/site-packages'
        ''.format(
            redhat_version=get_redhat_version(),
            rms_version='.'.join(get_rms_version()),
            python_version=python_version,
        )
    )
