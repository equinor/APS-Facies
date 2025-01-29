#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aps.utils.ConvertBitMapToRMS import ConvertBitMapToRMS
from aps.utils.constants.simple import Debug

long_help = """-------------------------------------------------------------------------------------
Converts a bitmap (8-bit) image file to a RMS irap map format file.

Purpose: Read a rectangular piece of a bitmap color file with 1byte colors (256 colors) and information
         about coordinates for the selected rectangle of the bitmap image and other
         information to be able to convert the bitmap image into
         an irap map format file that can be imported into RMS.
Input:   Bitmap input file (1 byte) colors (256 colors at maximum)
         Parameter file containing reference to coordinates of the rectangular area
         to be selected as well as which facies belongs to which colour number.
         Note that the selected rectangular area of the bitmap is specified with its corner point coordinates
         and pixel numbers.
Output:  An irap map file containing the colour/facies numbers for each pixel
         or facies number for each pixel.

Usage:
         1. Import the script into an empty python job in e.g.a an empty rms workflow.
            The rms python version and environment contains all python modules
            necessary to run the script or alternatively run the script from a shell script
            where the necessary environment variables are set automatically.
         2. Update the input model file to fit your case.

 Description of input parameter file which is a xml file:
 Example:
<?xml version="1.0" ?>
<ConvertBitmapToRMS>
 <Coordinates>
   <xmin>   480000  </xmin>
   <xmax>   493000  </xmax>
   <ymin>   6688000 </ymin>
   <ymax>   6710000 </ymax>
 </Coordinates>
 <PixelInterval>
   <nx> 476 </nx>
   <ny>  841 </ny>
   <I> 18 468 </I>
   <J> 9 769 </J>
 </PixelInterval>
 <CropToPixelInterval> 1 </CropToPixelInterval>
 <MissingCode> 9999900.000 </MissingCode>
 <UseFaciesCode>  1  </UseFaciesCode>
 <ColorCode facies="1"> 168 </ColorCode>
 <ColorCode facies="2"> 157 </ColorCode>
 <ColorCode facies="3"> 232 </ColorCode>
 <ColorCode facies="4"> 111 </ColorCode>
 <ColorCode facies="5"> 1 </ColorCode>
 <Files>
   <Input> CorelDraw_aboveFS36_model_input.bmp </Input>
   <Output> out1_facies.irap </Output>
 </Files>
 <Files>
   <Input> CorelDraw_aboveFS38_model_input.bmp </Input>
   <Output> out2_facies.irap </Output>
 </Files>
</ConvertBitmapToRMS>

 Explanation of keywords:
      Coordinates   -  specify coordinates for corner points of a rectangle in the map.
                       (xmin, ymin) corresponds to pixel (Imin, Jmin), and
                       (xmax, ymax) corresponds to pixel (Imax, Jmax),
                        where Imin, Imax, Jmin, Jmax is specified in keyword PixelInterval.
      PixelInterval -  specify number of pixels in the whole image and an
                       interval of pixels corresponding to the rectangle defined by the corner points.
                       Hence the user will have to identify the corner point pixels (Imin, Jmin), (Imax, Jmax)
                       and their corresponding geographic (UTM coordinates) (xmin, ymin) and (xmax ,ymax).
      UseFaciesCode -  Turn on (1) to use correspondence between color code and facies code to be able to write facies codes in output maps.
                       Turn off(0) use of facies code. This means output maps will contain color codes.
      ColorCode     -  specify which facies code corresponds to which color. The effect of this keyword is turned on/off by the keyword UseFaciesCode.
                       The user will usually have to run with UseFaciesCode turned off (0) to get output maps with colour values.
                       The user will then find corresponding colour values and facies
                       and then specify that using this keyword before running a second time. Missing code (usually 9999900.000) is
                       specified in separate keyword.
      CropToPixelInterval - Is set to 1 if the output maps should only contain the pixels in the specified rectangle. If it is set to 0
                            the script will calculate the geographic coordinates of pixel (1,1) and (nx,ny) and write out uncropped file
                            which also will contain area outside the specified rectangle.
      File          - Specify the input and output files.

      NOTE: It is important to note that xmin, ymin, xmax, ymax define coordinates for the pixels specified by the PixelInterval keyword.
--------------------------------------------------------------------------------------"""


def run(params):
    """
      Converts a 8-bit bitmap image file to RMS irap map format.
      Usage:
      - Specify a python disctionary with a model file containing all input. See example 1 for specification.
      - Specify a python dictionary with all input. See example 2 for specification.

    Example 1:
    from aps.toolbox import bitmap_to_rms
    from aps.utils.constants.simple import Debug

    params = {
       "model_file_name": "examples/bitmap2rms_facies_codes2.xml",
       "debug_level": Debug.VERBOSE,
    }

    bitmap_to_rms.run(params)


    Example 2:
    from aps.toolbox import bitmap_to_rms
    from aps.utils.constants.simple import Debug

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

    """
    debug_level = params['debug_level']
    bitmap_converter = ConvertBitMapToRMS(params)
    if debug_level >= Debug.ON:
        bitmap_converter.printContents()
    bitmap_converter.convert()
    bitmap_converter.writeFile()
    if debug_level >= Debug.ON:
        print('Finished: run_convert_bitmap_to_rms')
