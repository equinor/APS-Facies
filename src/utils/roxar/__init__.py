# -*- coding: utf-8 -*-
def running_in_batch_mode():
    try:
        import roxar.rms
    except ImportError:
        return False
    return roxar.rms.get_execution_mode() == roxar.ExecutionMode.Batch


def get_nrlib_path():
    try:
        import roxar.rms
    except ImportError:
        return None

    import platform
    import re

    description = platform.platform()
    if 'redhat' in description:
        # Assuming we are on RGS
        redhat_version = re.match(r'.*redhat-(?P<major>[0-9]+).*', description).groupdict()['major']
        rms_version = roxar.rms.get_version().split('.')[0]
        return '/project/res/nrlib/nrlib-dist-RHEL{}-RMS{}'.format(redhat_version, rms_version)
