import roxar
import roxar.rms
from aps.utils.constants.simple import Debug


def check_rms_execution_mode(debug_level: Debug = Debug.OFF):
    """
    Return True if RMS is run in batch model (using -batch) and False if run from RMS GUI.
    """
    mode = roxar.rms.get_execution_mode()
    if debug_level >= Debug.VERY_VERBOSE:
        print(f'--- RMS is run in {mode} mode')
    return mode == roxar.ExecutionMode.Batch
