# Test script reading input parameters from model file

from aps.toolbox import bitmap_to_rms
from aps.utils.constants.simple import Debug

print(f"Run script: {bitmap_to_rms.__file__}  ")

params = {
   "model_file_name": "examples/bitmap2rms_facies_codes2.xml",
   "debug_level": Debug.VERBOSE,
}

bitmap_to_rms.run(params)
