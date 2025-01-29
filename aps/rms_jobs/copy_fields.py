from pathlib import Path
from tempfile import TemporaryDirectory

from aps.rms_jobs.export_fields_to_disk import run as run_export_fields
from aps.rms_jobs.import_fields_from_disk import run as run_import_fields


def run(roxar=None, project=None, **kwargs):
    with TemporaryDirectory() as location:
        location = Path(location)
        run_export_fields(roxar, project, save_dir=location, **kwargs)
        run_import_fields(roxar, project, load_dir=location, **kwargs)


if __name__ == '__main__':
    import roxar

    run(roxar, project)
