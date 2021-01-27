#!/bin/env python
# -*- coding: utf-8 -*-
# Python3 script to update APS model file from global IPL include file
from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug
from aps.utils.roxar.fmu_tags import get_list_of_aps_uncertainty_parameters, set_selected_as_fmu_updatable
from aps.utils.methods import get_run_parameters, get_workflow_name, get_debug_level

"""
Description:
    This script uses Roxar API to read RMS table with parameters. The parameter names are specified using the
    RMS uncertainty functionality related to workflows, and uses the functionality 'Additional uncertainties' to
    add parameters  that is to be assigned values in the RMS uncertainty setup. NOTE: A requirement is that the
    naming convention that is adopted for FMU taggable variables in APS model files is used. This means that
    the naming of the parameters must follow the same rules as the name of the 'tagged' variables that
    is to be updated by FMU. If other names are used, they will be ignored and no updates of the model file will happen.

Example:
    Assume you want to use the RMS uncertainty module to update MainRange parameter for Gauss field GRF04 in zone number 2 and region number 4.
    The naming convention is then to use the variable name: APS_2_4_GF_GRF04_RESIDUAL_MAINRANGE
    The following must be done for the APS model to be updated:
    1. This variable name is used in the RMS uncertainty setup by using 'Additional uncertainties'.
    2. A probability distribution is specified for this variable in the uncertainty setup panel and a RMS table is created.
    3. The input to the updateAPSModelFromUncertainty script is the name of the RMS uncertainty table containing the generated values for the APS parameter
       and a list which in this example contain one variable name, the name 'APS_2_4_GF_GRF04_RESIDUAL_MAINRANGE'.
    4. The input APS mode must have the attribute  kw="APS_2_4_GF_GRF04_RESIDUAL_MAINRANGE" for the xml keyword for the parameter
       in the model file. (We also call this attribute a FMU tag).
       Usually the parameters in the model file to be updated is defined in the APSGUI as FMU tagged variable.
       It is also possible to tag the parameter manually by editing the APS model file or use a script to do that.
"""


def update_aps_model_from_uncertainty(
        project,
        input_aps_model_file,
        output_aps_model_file,
        workflow_name=None,
        write_output_file_with_parameter_names=False,
        debug_level=Debug.OFF,
        current_job_name=None,
):
    """ Script that get values for specified parameter names from a RMS uncertainty table with parameters and updates an APS model file.
        Input: project - The global variable project from Roxar API.
               rms_table_name - Name of RMS table containing values for the specified model parameters to be updated in APS model file.
               uncertainty_variable_names - List of names of the variables in the APS model to be updated.
               realisation_number - Which project realisation number in RMS is to be used.
               input_aps_model_file - Name of APS model file
               output_aps_model_file - Name of updated APS model file
    """
    print('Workflow name: {}'.format(workflow_name))
    if write_output_file_with_parameter_names and workflow_name:
        output_file_with_parameter_names = 'tmp_' + workflow_name + '.dat'
    else:
        output_file_with_parameter_names = None

    # Create empty APSModel object
    apsModel = APSModel()
    # Read model file and get parameter values from rms table and update values in xml tree but no data
    # is put into APSModel data structure but instead an updated XML data tree is returned.

    # Get current realisation
    realisation_number = project.current_realisation

    # Get uncertainty variables defined for the specified workflow which is specific for APS
    # The parameter name must start with APS_ and follow the standard for FMU tagged variables for APS
    uncertainty_variable_names = get_list_of_aps_uncertainty_parameters(project, workflow_name)
    debug_level = Debug.ON
    print('Specified APS model parameter names in RMS uncertainty table:')
    if debug_level >= Debug.ON:
        for s in uncertainty_variable_names:
            print(s)
        print('')
    # Tag all relevant parameters as FMU updatable and write out a new model file containing the tags
    set_selected_as_fmu_updatable(
        input_model_file=input_aps_model_file,
        output_model_file=output_aps_model_file,
        selected_variables=uncertainty_variable_names,
        tagged_variable_file=output_file_with_parameter_names,
    )

    # Read the values of the tagged variables from RMS table corresponding to the specified workflow
    # Use the tagged model file and update this file with new values and write it out again,
    # now with updated values for the tagged parameters
    eTree = apsModel.update_model_file(
        model_file_name=output_aps_model_file,
        parameter_file_name=None,
        project=project,
        workflow_name=workflow_name,
        uncertainty_variable_names=uncertainty_variable_names,
        realisation_number=realisation_number,
        debug_level=debug_level,
        use_rms_uncertainty_table=True,
        current_job_name=current_job_name
    )

    # Write the updated XML tree for the model parameters to a new file
    apsModel.write_model_from_xml_root(eTree, output_aps_model_file)


# -------  Main ----------------
def run(roxar=None, project=None, **kwargs):
    import roxar.rms
    params = get_run_parameters(**kwargs)
    input_aps_model_file = params['model_file']
    debug_level = get_debug_level(**kwargs)
    # workflow_name = get_workflow_name()
    workflow_name = params['workflow_name']
    output_aps_model_file = input_aps_model_file.replace('APS.xml', 'APS_modified.xml')
    write_output_file_with_parameter_names = False
    current_job_name = roxar.rms.get_running_job_name()
    if debug_level >= Debug.ON:
        print('Update model file {} from RMS uncertainty table {}'.format(input_aps_model_file, workflow_name))
        write_output_file_with_parameter_names = True

    update_aps_model_from_uncertainty(
        project, input_aps_model_file, output_aps_model_file, workflow_name,
        write_output_file_with_parameter_names, debug_level=debug_level, current_job_name=current_job_name
    )


if __name__ == '__main__':
    run()
