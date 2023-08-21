# Script to set switch whether to simulate and export field parameter
# or import field parameter
from pathlib import Path
from aps.utils.fmu import is_initial_iteration
from aps.utils.constants.simple import Debug
from fmu.config import utilities

# Read possible global switches relevant for simulating perm/poro fields
CFG = utilities.yaml_load("../../fmuconfig/output/global_variables.yml")["global"]

TOP_DIR = "../.."
WORKFLOW_NAME = "Update_perm_poro"
WORKFLOW = project.workflows[WORKFLOW_NAME]
JOB_NAMES_INITIAL =[
    "sim_perm_poro",
    "Resample_to_ertbox",
    "Export_A3_perm",
    "Export_C_perm",
    "Export_A3_poro",
    "Export_C_poro",
    ]
JOB_NAMES_UPDATE =[
    "Resample_from_ertbox",
    "A3_perm",
    "C_perm",
    "A3_poro",
    "C_poro",
    ]

DEBUG_LEVEL = Debug.ON

def check_ert_iteration():
    '''
    Check if folder with name equal to a non-negative integer exists.
    If a folder with name 0 is found or no folder with integer exists,
    the APS mode is to simulate and export GRF files to be used in ERT
    and this function return True.
    If a folder with name 1 or 2 or 3 or ... MAXITER is found,
    the APS mode is import updated GRF from ERT and this function return False
    '''
    MAXITER = 100
    toplevel = Path(TOP_DIR)
    iterfolder = -1
    for folder in range(MAXITER):
        if (toplevel / str(folder)).exists():
            iterfolder = folder
            break
    if DEBUG_LEVEL >= Debug.ON:
        print(f"- ERT iteration: {iterfolder} ")
    return iterfolder <= 0

def main():
    is_initial = check_ert_iteration()

    # Jobs to run to create per/poro fields
    for job_name in JOB_NAMES_INITIAL:
        WORKFLOW.jobs.set_active(job_name, is_initial)
        if DEBUG_LEVEL >= Debug.ON:
            if is_initial:
                print(f"- Set active job:{job_name}")
            else:
                print(f"- Set inactive job:{job_name}")
    for job_name in JOB_NAMES_UPDATE:
        not_initial = not is_initial
        WORKFLOW.jobs.set_active(job_name, not_initial)
        if DEBUG_LEVEL >= Debug.ON:
            if not is_initial:
                print(f"- Set active job:{job_name}")
            else:
                print(f"- Set inactive job:{job_name}")



if __name__ == "__main__":
        main()


