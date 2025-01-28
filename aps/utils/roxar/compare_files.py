# -*- coding: utf-8 -*-
from aps.utils.checks import compare
from aps.utils.io import write_status_file


def run(roxar=None, project=None, **kwargs):
    file_name1 = kwargs.get(
        'file_name1', 'examples/reference_uncertainty_parameter_list.dat'
    )
    file_name2 = kwargs.get('file_name2', 'tmp_Test_APS_uncertainty_workflow.dat')

    print(f'Compare file: {file_name1} and {file_name2}')
    check = compare(file_name1, file_name2)

    write_status_file(check)
    assert check is True


if __name__ == '__main__':
    run()
