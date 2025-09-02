---
title: Convert bitmap to RMS surface format
---
## Utility script to convert 8-bit bitmap file to RMS surface file format

**Description**: Python script to convert a 8-bit bitmap file to RMS readable 2D map file. Purpose is to get hand-drawn maps into RMS as part of building 3D deterministic facies parameters.

**Dependency**: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**: Bitmap files, coordinates for positioning of the bitmap, grid resolution.

**Output**: RMS readable files for maps from hand-drawn maps.

The utility script `bitmap_to_rms.py`:

**Alternative ways to implement the use of this script:**

- Make your own Python script, define all input in your script with
 an input dictionary and call the utility scripts run function with the input dictionary

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

**NOTE**: Use the Python script as a Python job in RMS since it applies the API `rmsapi` from RMS.

### Example of a Python script using a yml configuration file (model file) as input

In this case the input data directory contains the keyword `model_file_name` to specify the input yml configuration file.

```python
from aps.toolbox import bitmap_to_rms
from aps.utils.constants.simple import Debug


print(f"Run script: {bitmap_to_rms.__file__}")

params = {
    "model_file_name": "example_input/bitmap2rms_facies_codes.yml",
    "debug_level": Debug.VERBOSE,
}

bitmap_to_rms.run(params)
```

### Example 1 yml file format
This example is a yml file as input to the bitmap_to_rms.py script.

It converts 3 files and use a colorcode to facies code mapping to get the results with facies codes.

Note that the specified pixel interval define which pixels to be used.
The lower left corner point of the pixel interval corresponds to the lower left x,y coordinate.

The specified coordinate intervals should correspond to the localisation of the pixel interval chosen from the bitmaps.

It is possible to convert the bitmap into RMS file format with colorcode as values or facies code as values,
but the user have to identify which color codes represents which facies codes through the mapping specified by the keyword `ColorCode`.

```yaml
bitmap2rms:
  Coordinates:
    x:  643400  658400
    y: 4343950 4359800
  PixelInterval:
    nx: 1152
    ny: 1152
    I: 220 770
    J: 550 1100
  CropToPixelInterval: True
  MissingCode: 9999900.000
  UseFaciesCode: True
  ColorCode:
    1: 232
    2: 113
    3:  79
    4: 251
  Files:
    - Input: examples/img/bitmap/B1.bmp
      Output: B1.irap
    - Input: examples/img/bitmap/B2.bmp
      Output: B2.irap
    - Input: examples/img/bitmap/B3.bmp
      Output: B3.irap
```

### Example of a Python script where all input is specified in the script
In this case the input data directory contains all relevant keywords to specify the input to the script.
Note that in this case the keyword `model_file_name` is not used.

```python
from aps.toolbox import bitmap_to_rms
from aps.utils.constants.simple import Debug

print(f"Run script: {bitmap_to_rms.__file__}")

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
        "Iend": 770,
        "Jstart": 550,
        "Jend": 1100,
    },
    "ColorCodeMapping": {
        1: 232,
        2: 113,
        3:  79,
        4: 251,
    },
    "CropToPixelInterval": True,
    "MissingCode": 9999900.000,
    "UseFaciesCode": True,
    "InputFileList": [
        "examples/img/bitmap/B1.bmp",
        "examples/img/bitmap/B2.bmp",
        "examples/img/bitmap/B3.bmp",
    ],
    "OutputFileList": [
        "B1_test2.irap",
        "B2_test2.irap",
        "B3_test2.irap",
    ]
}

bitmap_to_rms.run(params)
```
