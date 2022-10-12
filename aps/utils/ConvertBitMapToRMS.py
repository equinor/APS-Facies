#!/bin/env python
# -*- coding: utf-8 -*-
"""-------------------------------------------------------------------------------------
python3 script which can be run as a python job in RMS10
Purpose: Read a rectangular piece of a bitmap color file with 1byte colors (256 colors) and information
         about coordinates for the selected rectangle of the bitmap image and other
         information to be able to convert the bitmap image into
         an irap map format file that can be imported into RMS.
Input:   Bitmap input file (1byte) colors (256 colors at maximum)
         Parameter file containing reference to coordinates of the rectangular area
         to be selected as well as which facies belongs to which color number.
         Note that the selected rectangular area of the bitmap is specified with its corner point coordinates
         and pixel numbers.
Output:  An irap map file containing the color numbers for each pixel
         or facies number for each pixel.

Usage:
         1. Import the script into an empty python job in e.g.a an empty rms workflow.
            The rms10 python version and environment contains all python modules
            necessary to run the script.
         2. The user replace the input files in the script by the correct input files
            for both the bitmap file and parameter specification file.
            Search for "User specified input variables" in this script to find the location
            for the user specific input file names.
         3. Specify the parameter file which will tell the script about the geographical
            coordinates for location of the picture, the rectangular area of the picture
            to be used and the relation between color numbers and facies.
         4. Since the script cannot know the relation between color and facies apriori
            the user first have to specify the parameter file without specifying
            color - facies correspondence. The result will then be a map file with
            color values as 2D grid cell values. The the user visualise the map file
            and find which color number actually corresponds to each facies. This
            information is specified in the parameter file and the script is
            re-run once more. Now the output map should contain the specified
            facies codes instead of color codes.

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
   <I> 19 465 </I>
   <J> 10 769 </J>
 </PixelInterval>
 <ColorCode facies="1"> 111 </ColorCode>
 <ColorCode facies="2"> 232 </ColorCode>
 <ColorCode facies="3"> 157 </ColorCode>
 <ColorCode facies="6"> 168 </ColorCode>
</ConvertBitmapToRMS>

 Explanation of keywords:
      Coordinates   -  specify coordinates for corner points of a rectangle in the map
      PixelInterval -  specify number of pixels in the whole image and an
                       interval of pixels corresponding to the rectangle defined by the corner points.
                       Hence the user will have to identify the four corner point pixels
                       and their corresponding geographic (UTM coordinates).
      FaciesCodes   -  specify which facies code corresponds to which color. This keyword is optional,
                       and the user will usually have to run without this keyword first to get a map
                       with color values. Find corresponding color values and facies
                       and then specify that using this keyword before running a second time.
--------------------------------------------------------------------------------------"""
import copy
import xml.etree.ElementTree as ET
import os
from pathlib import Path

import numpy as np
from PIL import Image

from aps.utils.constants.simple import Debug
from aps.utils.methods import get_colors, check_missing_keywords_dict, check_missing_keywords_list
from aps.utils.ymlUtils import (get_text_value, get_bool_value,
    get_float_value, get_dict, get_int_value, get_list, readYml)

def isOneByteColor(c):
    try:
        int(c)
    except:
        return False
    else:
        return True


def isThreeByteColor(c):
    try:
        [v1, v2, v3] = c
    except:
        return False
    else:
        return True


def writeIrapMap(fmap, xOrigo, yOrigo, xinc, yinc, angleInDegrees, outputFileName):
    rows = fmap.shape[0]
    cols = fmap.shape[1]
    nx = cols
    ny = rows

    with open(outputFileName, 'w') as file:
        line = ' -996 ' + str(ny) + '  ' + str(xinc) + '  ' + str(yinc) + str('\n')
        file.write(line)

        xm = xOrigo + (nx - 1) * xinc
        ym = yOrigo + (ny - 1) * yinc
        line = '  ' + str(xOrigo) + '  ' + str(xm) + '  ' + str(yOrigo) + '  ' + str(ym) + str('\n')
        file.write(line)

        line = '  ' + str(nx) + '  ' + str(angleInDegrees) + '  ' + str(xOrigo) + '  ' + str(yOrigo) + str('\n')
        file.write(line)

        line = ' 0   0   0   0   0   0   0 \n'
        file.write(line)

        n = 0
        line = ' '
        for j in range(ny):
            jj = ny - 1 - j
            for i in range(nx):
                line = line + str(fmap[jj, i]) + '  '
                n = n + 1
                if n == 6:
                    line = line + str('\n')
                    file.write(line)
                    n = 0
                    line = ' '
        if n > 0:
            file.write(line)
        print('\n')


class ConvertBitMapToRMS:
    def __init__(self, params ):
        self.__model_file_name =  params.get('model_file_name', None)
        debug_level = params.get('debug_level', Debug.OFF)

        # Internal variables,  not to be set here, but used in algorithm
        self.__faciesCode = []
        self.__colorCode =[]
        self.__fmapFaciesList = []
        self.__fmapColorsList = []

        # Read model file if it is defined or assign values from input dict
        if self.__model_file_name is not None:
            print(f'Model file: {self.__model_file_name}')
            self.read_model_file(debug_level=debug_level)
        else:
            # Check that all necessary parameters are set when not using model file
            required_kw_dict = {
                "Coordinates": ["xmin", "xmax", "ymin", "ymax"],
                "PixelInterval": ["nx", "ny", "Istart", "Jstart", "Iend", "Jend"],
            }
            required_kw_list = [
                "ColorCodeMapping",
                "CropToPixelInterval",
                "MissingCode",
                "UseFaciesCode",
                "InputFileList",
                "OutputFileList",
            ]
            check_missing_keywords_dict(params, required_kw_dict)

            for kw in required_kw_dict:
                missing_kw = []
                for kw2 in required_kw_dict[kw]:
                    if kw2 not in params[kw]:
                        missing_kw.append(kw2)
                if len(missing_kw) > 0:
                    raise ValueError(f"Missing sub keywords: {missing_kw} in {kw} ")

            check_missing_keywords_list(params, required_kw_list)

            # Assigned from user input
            self.__nx = params['PixelInterval']['nx']
            self.__ny = params['PixelInterval']['ny']
            self.__iStart = params['PixelInterval']['Jstart']
            self.__iEnd = params['PixelInterval']['Jend']
            self.__jStart = params['PixelInterval']['Istart']
            self.__jEnd = params['PixelInterval']['Iend']
            self.__xOrigo = params['Coordinates']['xmin']
            self.__yOrigo = params['Coordinates']['ymin']
            self.__xMax = params['Coordinates']['xmax']
            self.__yMax = params['Coordinates']['ymax']
            self.__missingCode = params['MissingCode']
            self.__crop = params['CropToPixelInterval']
            self.__inputFileList = params['InputFileList']
            self.__outputFileList = params['OutputFileList']
            self.__faciesCode = list(params['ColorCodeMapping'].keys())
            self.__colorCode = list(params['ColorCodeMapping'].values())

            # Internal use
            mx = self.__jEnd - self.__jStart + 1
            my = self.__iEnd - self.__iStart + 1
            self.__xinc = (self.__xMax - self.__xOrigo) / mx
            self.__yinc = (self.__yMax - self.__yOrigo) / my


    def read_model_file(self, debug_level=Debug.OFF):
        # Check suffix of file for file type
        model_file = Path(self.__model_file_name)
        suffix = model_file.suffix.lower().strip('.')
        if suffix in ['yaml', 'yml']:
            self.__read_model_file_yml(debug_level=debug_level)
        elif suffix == 'xml':
            self.__read_model_file_xml(debug_level=debug_level)
        else:
            raise ValueError(f"Model file name: {self.__model_file_name}  must be either 'xml' or 'yml' format")


    def __read_model_file_yml(self, debug_level=Debug.OFF):

        if debug_level >= Debug.ON:
            print(f'Read file: {self.__model_file_name}')

        spec_all = readYml(self.__model_file_name)

        kw = 'bitmap2rms'
        spec = spec_all[kw] if kw in spec_all else None
        if spec is None:
            raise ValueError(f"Missing keyword: {kw} ")

        coord = get_dict(spec, 'bitmap2rms', 'Coordinates')
        text = get_text_value(coord, 'Coordinates','x')
        [xmin, xmax] = text.split()
        self.__xOrigo = float(xmin)
        self.__xMax = float(xmax)
        text = get_text_value(coord, 'Coordinates','y')
        [ymin,ymax] = text.split()
        self.__yOrigo = float(ymin)
        self.__yMax = float(ymax)

        kw = 'PixelInterval'
        pixinterval = get_dict(spec, 'bitmap2rms', 'PixelInterval')
        self.__nx = get_int_value(pixinterval, 'PixelInterval', 'nx')
        self.__ny = get_int_value(pixinterval, 'PixelInterval', 'ny')
        text = get_text_value(pixinterval, 'PixelInterval', 'I')
        [Istart, Iend] = text.split()
        self.__jStart = int(Istart)
        self.__jEnd = int(Iend)
        text = get_text_value(pixinterval, 'PixelInterval', 'J')
        [Jstart, Jend] = text.split()
        self.__iStart = int(Jstart)
        self.__iEnd = int(Jend)

        if self.__iStart < 1 or self.__iEnd > self.__ny:
            raise ValueError(
                f"Error: Pixel interval in y direction ({self.__iStart},{self.__iEnd}) "
                f"is not within {1} and {self.__ny}"
            )

        if self.__jStart < 1 or self.__jEnd > self.__nx:
            raise ValueError(
                f"Error: Pixel interval in y direction ({self.__jStart},{self.__jEnd}) "
                f"is not within {1} and {self.__nx}"
            )


        self.__crop = get_bool_value(spec, 'CropToPixelInterval', True)
        use_facies_code = get_bool_value(spec, 'UseFaciesCode', False)

        if use_facies_code:

            self.__missingCode = get_float_value(spec, 'bitmap2rms', 'MissingCode')

            color_code_per_facies = get_dict(spec, 'bitmap2rms', 'ColorCode')
            facies_codes = list(color_code_per_facies.keys())
            color_codes = list(color_code_per_facies.values())
            if debug_level >= Debug.VERBOSE:
                print(f"-- faciesCodes: {facies_codes} ")
                print(f"-- colorcodes: {color_codes} ")
            if len(facies_codes) > 0:
                self.__faciesCode = facies_codes
                self.__colorCode = color_codes

        file_dict_list = get_list(spec, 'bitmap2rms', 'Files')
        self.__inputFileList = []
        self.__outputFileList = []
        for file_dict in file_dict_list:
            input_file = file_dict['Input']
            output_file = file_dict ['Output']
            if debug_level >= Debug.VERBOSE:
                print(f"-- Input file: {input_file} ")
                print(f"-- Output file: {output_file} ")
            self.__inputFileList.append(input_file)
            self.__outputFileList.append(output_file)

        mx = self.__jEnd - self.__jStart + 1
        my = self.__iEnd - self.__iStart + 1
        self.__xinc = (self.__xMax - self.__xOrigo) / mx
        self.__yinc = (self.__yMax - self.__yOrigo) / my

    def __read_model_file_xml(self, debug_level=Debug.OFF):

        if debug_level >= Debug.ON:
            print(f'Read file: {self.__model_file_name}')
        if not os.path.exists(self.__model_file_name):
            raise IOError(f"File {self.__model_file_name} does not exist")

        tree = ET.parse(self.__model_file_name)
        self.__ET_Tree = tree
        root = tree.getroot()

        # --- Coordinates ---
        kw = 'Coordinates'
        obj = root.find(kw)
        if obj is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        kw = 'xmin'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        self.__xOrigo = float(text.strip())

        kw = 'xmax'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        self.__xMax = float(text.strip())

        kw = 'ymin'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        self.__yOrigo = float(text.strip())

        kw = 'ymax'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        self.__yMax = float(text.strip())

        # --- PixelInterval ---
        kw = 'PixelInterval'
        obj = root.find(kw)
        if obj is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )

        kw = 'nx'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        self.__nx = int(text.strip())

        kw = 'ny'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        self.__ny = int(text.strip())

        kw = 'I'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )
        text = obj2.text
        [text1, text2] = text.split()
        self.__jStart = int(text1.strip())
        self.__jEnd = int(text2.strip())

        kw = 'J'
        obj2 = obj.find(kw)
        if obj2 is None:
            raise IOError(
                f'Error reading model file {self.__model_file_name}. Missing command: {kw}'
            )

        text = obj2.text
        [text1, text2] = text.split()
        self.__iStart = int(text1.strip())
        self.__iEnd = int(text2.strip())

        if self.__iStart < 1:
            raise ValueError(
                'Error: Pixel interval in y direction ' + '(' + str(self.__iStart) + ',' + str(self.__iEnd) + ')'
                ' is not within ' + str(1) + ' and ' + str(self.__ny)
            )

        if self.__jStart < 1:
            raise ValueError(
                'Error: Pixel interval in x direction ' + '(' + str(self.__jStart) + ',' + str(self.__jEnd) + ')'
                ' is not within ' + str(1) + ' and ' + str(self.__nx)
            )

        if self.__iEnd > self.__ny:
            raise ValueError(
                'Error: Pixel interval in y direction ' + '(' + str(self.__iStart) + ',' + str(self.__iEnd) + ')'
                ' is not within ' + str(1) + ' and ' + str(self.__ny)
            )

        if self.__jEnd > self.__nx:
            raise ValueError(
                'Error: Pixel interval in x direction ' + '(' + str(self.__jStart) + ',' + str(self.__jEnd) + ')'
                ' is not within ' + str(1) + ' and ' + str(self.__nx)
            )

        kw = 'CropToPixelInterval'
        obj = root.find(kw)
        if obj is not None:
            text = obj.text
            self.__crop = bool(text.strip())

        kw = 'UseFaciesCode'
        define_facies_code = False
        obj = root.find(kw)
        if obj is not None:
            text = obj.text
            if int(text) != 0:
                define_facies_code = True

        if define_facies_code:
            kw = 'MissingCode'
            obj = root.find(kw)
            if obj is None:
                raise IOError(
                    f'Error reading model file {self.__model_file_name}. Missing command {kw}'
                )

            text = obj.text
            self.__missingCode = float(text.strip())

            # --- ColorCode ---
            kw = 'ColorCode'
            faciesCode = []
            colorCode = []
            for obj in root.findall(kw):
                if obj is None:
                    raise IOError(f"Error reading model file {self.__model_file_name}. Missing command: {kw}")
                fCode = int(obj.get('facies'))
                cCode = int(obj.text.strip())
                faciesCode.append(fCode)
                colorCode.append(cCode)
            if len(faciesCode) > 0:
                self.__faciesCode = faciesCode
                self.__colorCode = colorCode

        # --- Files ---
        self.__inputFileList = []
        self.__outputFileList = []
        kw = 'Files'
        for obj in root.findall(kw):
            if obj is None:
                raise IOError(f"Error reading model file {self.__model_file_name}. Missing command: {kw}")
            kw1 = 'Input'
            obj2 = obj.find(kw1)
            if obj2 is None:
                raise IOError(f"Error reading model file {self.__model_file_name}. Missing command: {kw1}")
            text = obj2.text
            self.__inputFileList.append(text.strip())
            kw2 = 'Output'
            obj3 = obj.find(kw2)
            if obj3 is None:
                raise IOError(f"Error reading model file {self.__model_file_name}. Missing command: {kw2}")
            text = obj3.text
            self.__outputFileList.append(text.strip())

        mx = self.__jEnd - self.__jStart + 1
        my = self.__iEnd - self.__iStart + 1
        self.__xinc = (self.__xMax - self.__xOrigo) / mx
        self.__yinc = (self.__yMax - self.__yOrigo) / my

    @property
    def nFacies(self):
        return len(self.__faciesCode)

    def printContents(self):
        print(' xmin: ' + str(self.__xOrigo))
        print(' ymin: ' + str(self.__yOrigo))
        print(' xinc: ' + str(self.__xinc))
        print(' yinc: ' + str(self.__yinc))
        print(' nx (ncol): ' + str(self.__nx))
        print(' ny (nrow): ' + str(self.__ny))
        print(' iStart: ' + str(self.__jStart))
        print(' iEnd: ' + str(self.__jEnd))
        print(' jStart: ' + str(self.__iStart))
        print(' jEnd: ' + str(self.__iEnd))
        if np.abs((self.__xinc - self.__yinc) / self.__xinc) > 0.05:
            print('Warnings:')
            print(' Pixel dimension (xinc, yinc) is different in x and y direction. Is this correct?')
            print(' Or are there something wrong with the coordinates that are specified?')

        if self.nFacies > 0:
            print('')
            print('Missing code for facies is set to: ' + str(self.__missingCode))
            print('')
            print('FaciesCode   ColorCode')
            for i in range(self.nFacies):
                print('   ' + str(self.__faciesCode[i]) + '          ' + str(self.__colorCode[i]))

    def convert(self):
        self.__fmapFacies = []
        for fileName in self.__inputFileList:
            print(f'Read file: {fileName}')
            ncolSpecified = self.__nx
            nrowSpecified = self.__ny
            path = Path(fileName)
            if not path.exists():
                if self.__model_file_name is not None:
                    path = Path(self.__model_file_name).parent / fileName
                else:
                    path = "./" + fileName
            im = Image.open(path)

            fmapColors = np.array(im)

            c = fmapColors[0, 0]
            if isOneByteColor(c):
                print('Color is specified by 1 byte')
            else:
                if isThreeByteColor(c):
                    raise ValueError(
                        'Error: Number of bytes per pixel is not 1 but 3\n'
                        '       This conversion script requires that color depth is 8 bit not 24 bit'
                    )
                else:
                    raise ValueError('Error: Unknown input format')

            nrows = fmapColors.shape[0]
            ncols = fmapColors.shape[1]
            if nrows != nrowSpecified or ncols != ncolSpecified:
                raise ValueError(
                    'Error: Number of pixel specified in grid definition is different from the number of pixels in the map\n'
                    '       Number of pixels in bitmap file: (nx,ny) = ({ncols}, {nrows})\n'
                    '       Number of pixels specified:      (nx,ny) = ({ncolSpecified}, {nrowSpecified})'
                    ''.format(ncols=ncols, nrows=nrows, ncolSpecified=ncolSpecified, nrowSpecified=nrowSpecified)
                )

            if self.__crop:
                fmapColorsCropped = self.__cropMap(fmapColors)
                self.__fmapColorsList.append(fmapColorsCropped)
            else:
                self.__fmapColorsList.append(fmapColors)

            if self.nFacies > 0:
                # Initialize mapping function between color code and facies to missing code for all colors.
                self.__codeMapping = np.zeros(256, np.int)
                for n in range(256):
                    self.__codeMapping[n] = self.__missingCode

                maxFaciesCode = 0
                for i in range(self.nFacies):
                    c = self.__colorCode[i]
                    f = self.__faciesCode[i]
                    self.__codeMapping[c] = f
                    if maxFaciesCode < f:
                        maxFaciesCode = f

                fmapFacies = np.zeros((nrows, ncols))

                # Renumber the color  code to facies code
                for j in range(ncols):
                    for i in range(nrows):
                        c = fmapColors[i, j]
                        f = self.__codeMapping[c]
                        fmapFacies[i, j] = f

                if self.__crop:
                    fmapFaciesCropped = self.__cropMap(fmapFacies)
                    self.__fmapFaciesList.append(fmapFaciesCropped)
                else:
                    self.__fmapFaciesList.append(fmapFacies)

    @property
    def xminUnCropped(self):
        return self.__xOrigo - self.__xinc * (self.__jStart - 1)

    @property
    def xmaxUnCropped(self):
        return self.__xMax + self.__xinc * (self.__nx - self.__jEnd)

    @property
    def yminUnCropped(self):
        return self.__yOrigo - self.__yinc * (self.__iStart - 1)

    @property
    def ymaxUnCropped(self):
        return self.__yMax + self.__yinc * (self.__ny - self.__iEnd)

    def __cropMap(self, fmap):
        nrowsNew = self.__iEnd - self.__iStart + 1
        ncolsNew = self.__jEnd - self.__jStart + 1
        iiStart = self.__ny - self.__iEnd
        jjStart = self.__jStart - 1
        fmapNew = np.zeros((nrowsNew, ncolsNew))
        for j in range(ncolsNew):
            for i in range(nrowsNew):
                ii = iiStart + i  # The grid counts the pixel in y direction from top to bottom
                jj = jjStart + j
                fmapNew[i, j] = fmap[ii, jj]
        return fmapNew

    def writeFile(self):
        if self.__crop:
            xmin = self.__xOrigo
            ymin = self.__yOrigo
        else:
            xmin = self.xminUnCropped
            ymin = self.yminUnCropped

        n = 0
        for fileName in self.__outputFileList:
            print(f'Write file: {fileName}')
            angleInDegrees = 0.0
            if self.nFacies == 0:
                angleInDegrees = 0.0
                print('Write file with color code as grid values.')
                writeIrapMap(self.__fmapColorsList[n], xmin, ymin, self.__xinc, self.__yinc, angleInDegrees, fileName)
            else:
                print('Write file with facies code as grid values for specified colors and missing code elsewhere.')
                writeIrapMap(self.__fmapFaciesList[n], xmin, ymin, self.__xinc, self.__yinc, angleInDegrees, fileName)
            n += 1

    def testPlot(self):
        import matplotlib.colors
        import matplotlib.pyplot as plt

        nFacies = self.nFacies
        if nFacies == 0:
            return

        fig = plt.figure(figsize=[10.0, 7.5])
        nFacies = nFacies + 1
        # --- DefineColormaps from a list ---
        # Choose some default colors depending on number of facies
        colors = get_colors(nFacies)

        cmap_name = 'Colormap'
        # Create the colormap
        if nFacies > 0:
            cm = matplotlib.colors.ListedColormap(colors, name=cmap_name, N=nFacies)

        # Facies map is plotted
        ax = plt.subplot(2, 1, 1)
        if nFacies > 0:
            fmapFacies = copy.deepcopy(self.__fmapFaciesList[0])
            im2 = ax.imshow(fmapFacies, interpolation='none', origin='upper', cmap=cm)
        else:
            fmapColors = copy.deepcopy(self.__fmapColorsList[0])
            im2 = ax.imshow(fmapColors, interpolation='none', origin='upper')

            # Color legend for the truncation map and facies plots
        cax2 = fig.add_axes([0.90, 0.05, 0.02, 0.4])
        fig.colorbar(im2, cax=cax2)

        plt.show()
