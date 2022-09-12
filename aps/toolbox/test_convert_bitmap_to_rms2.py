# Test script reading input parameters from model file

from aps.toolbox import bitmap_to_rms
from aps.utils.constants.simple import Debug

print(f"Run script: {bitmap_to_rms.__file__}  ")

params = {
   "debug_level": Debug.VERBOSE,
   "Coordinates": {
      "xmin": 643400,
      "xmax": 658400,
      "ymin": 4343950,
      "ymax": 4359800,
   },
   "PixelInterval": {
      "nx": 1152,
      "ny": 1152,
      "Istart": 220,
      "Iend":   770,
      "Jstart": 550,
      "Jend":   1100,
   },
   "ColorCodeMapping": {
      1: 232,
      2: 113,
      3: 79,
      4: 251,
   },
   "CropToPixelInterval": True,
   "MissingCode": 9999900.000,
   "UseFaciesCode": True,
   "InputFileList":[
      "examples/img/bitmap/B1.bmp",
      "examples/img/bitmap/B2.bmp",
      "examples/img/bitmap/B3.bmp",
   ] ,
   "OutputFileList": [
      "B1_test2.irap",
      "B2_test2.irap",
      "B3_test2.irap",
   ]
}

bitmap_to_rms.run(params)
