# -*- coding: utf-8 -*-
from src.unit_test.helpers import compare

file_name1 = 'examples/reference_uncertainty_parameter_list.dat'
file_name2 = 'tmp_Test_APS_uncertainty_workflow.dat'

print('Compare file: ' + file_name1 + ' and ' + file_name2)
if  compare(file_name1, file_name2):
    print('Files are equal. OK')
else:
    raise AssertionException('Files are different. NOT OK')

