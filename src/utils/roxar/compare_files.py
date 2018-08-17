# -*- coding: utf-8 -*-
from src.unit_test.helpers import compare


def run(roxar=None, project=None, **kwargs):
    file_name1 = 'examples/reference_uncertainty_parameter_list.dat'
    file_name2 = 'tmp_Test_APS_uncertainty_workflow.dat'

    print('Compare file: ' + file_name1 + ' and ' + file_name2)
    check = compare(file_name1, file_name2)

    if check:
        print('Files are equal. OK')
    else:
        print('Files are different. NOT OK')
        assert check is True


if __name__ == '__main__':
    run()
