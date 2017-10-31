#!/bin/env python
"""
Dependency: ROXAPI
Python 3 truncation script to be run in RMS 10 workflow
Input:
      XML model file.
Output:
      Facies realisation updated for specified zones.
      Updated 3D parameter for transformed gaussian fields.
"""

import importlib

import numpy as np

import src.generalFunctionsUsingRoxAPI as gr
from src import (APSModel, APSZoneModel, Trend3D_linear)
from src.utils.constants.simple import Debug

importlib.reload(APSModel)
importlib.reload(APSZoneModel)
importlib.reload(Trend3D_linear)

# Initialise common variables
functionName = 'APS_main.py'

# Tolerance
eps = 0.000001


def findDefinedCells(zoneValues, zoneNr, debug_level=Debug.SOMEWHAT_VERBOSE):
    """
    For specified zoneNumber, identify which cells belongs to this zone.
    :param zoneValues:  Vector with zone values. The length is the same as the
                          number of active cells (physical cells) in the whole 3D grid.
    :param zoneNr:      The zone number (counting from 1) for which this
                          transformation should be applied. Only the cells belonging to the
                          zone with zoneNr is considered here.
    :param debug_level:
    :returns: (nDefinedCells, cellIndexDefined)
        WHERE
        int nDefinedCells Number of active (physical cells) belonging to the specified zone.
        list cellIndexDefined Index array. The length is nDefinedCells. The content is cell index which
                                is used in the grid parameter vectors zoneValue, gaussField, alpha and all
                                other parameter vectors containing cell values for
                                the active (physical) cells for the grid.
    """
    functionName = 'findDefinedCells'
    nDefinedCells = 0
    cellIndexDefined = []
    nCellsTotal = len(zoneValues)

    y1_defined = []
    for i in range(nCellsTotal):
        if zoneValues[i] == zoneNr:
            cellIndexDefined.append(i)
            nDefinedCells += 1

    if debug_level >= Debug.VERY_VERBOSE:
        print('Debug output: In findDefinedCells: Number of active cells for current zone: ' + str(nDefinedCells))

    return (nDefinedCells, cellIndexDefined)


def transformEmpiric(nDefinedCells, cellIndexDefined, gaussValues, alphaValues):
    """
    For the defined cells, transform the input Gaussian fields by the
    cumulative empiric distribution to get uniform distribution of the cells.
    The result is assigned to the input vectors alpha which also is returned.
    :param nDefinedCells: Number of active (physical cells). Is the length of
                          list cellIndexDefined.
    :type nDefinedCells: int
    :param cellIndexDefined: Index array. The length is nDefinedCells.
                             The content is cell index which is used in the
                             grid parameter vectors zoneValue, gaussField,
                             alpha and all other parameter vectors containing
                             cell values for the active (physical) cells for the grid.
    :type cellIndexDefined: list
    :param gaussValues: Gaussian fields to be transformed. The length is the
                        same as the list of defined cells. Only the cells
                        belonging to the specified list in cellIndexDefined
                        are considered here.
    :param alphaValues: Transformed gaussian fields. The length is the same as
                        the cellIndexDefined list. The input values in the
                        alpha vectors are updated for those cells that belongs
                        to specified cellIndexDefined list.
    :return: The updated alpha vector is returned. Only cells belonging to
             list in cellIndexDefined are modified compared with the values
             the vector had as input.
    """
    functionName = 'transformEmpiric'
    nCellsTotal = len(gaussValues)

    y1_defined = []
    for i in range(nDefinedCells):
        indx = cellIndexDefined[i]
        y1_defined.append(gaussValues[indx])

    sort_indx = np.argsort(y1_defined)
    for i in range(nDefinedCells):
        indx = sort_indx[i]
        # Assign the probability p= i/N to the cell corresponding to y1_defined cell 
        # with number i in sorting from smallest to highest value. 
        # Use cellIndexDefined to assign it to the correct cell.
        alphaValues[cellIndexDefined[indx]] = float(i) / float(nDefinedCells)

    return alphaValues


def checkAndNormaliseProb(
        nFacies, probParamValuesForFacies, useConstProb, nDefinedCells, cellIndexDefined,
        eps=0.0000001, debug_level=Debug.SOMEWHAT_VERBOSE
):
    """
    Check that probability cubes or probabilities in input probFacies is
    normalised. If not normalised, a normalisation is done. The list
    cellIndexDefined is an index vector. The length is in general less than
    the total number of active cells for the grid. Typically the
    cellIndexDefined vector represents active cells belonging to a specified
    zone, but could in principle be any subset of interest of the total set of
    all active cells. The content of the cellIndexDefined array is indices in
    vectors containing all active cells and is a way of defining a subset of
    cells.
    :param nFacies: the number of facies
    :type nFacies: int
    :param probParamValuesForFacies: A list of vectors where each vector
                                     represents probabilities for active grid
                                     cells. The first entry corresponds to the
                                     first facies in the facies list and so on.
                                     [fName,values] = probParamValuesForFacies[f]
                                     where fName is facies name and values is
                                     the probability values per cell.
                                     Note: If useConstProb = 1, the values
                                     list has one element only. and represent
                                     a constant facies probability.
                                     If useConstProb = 0, the values is a list
                                     of probabilities, one per grid cell.
    :type probParamValuesForFacies: list
    :param useConstProb: Is True if probParamValuesForFacies contains constant
                         probabilities and False if probParamValuesForFacies
                         contains vectors of probabilities, one value per
                         active grid cell.
    :type useConstProb: bool
    :param nDefinedCells: Length of the vector cellIndexDefined.
    :type nDefinedCells: int
    :param cellIndexDefined: A vector containing indices. cellIndexDefined[i]
                             is an index in the probability vectors in
                             probParamValuesForFacies. It is a way to defined
                             a filter of grid cells, a subset of all active
                             grid cells in the grid.
    :type cellIndexDefined: list
    :param eps: # TODO
    :param debug_level: Define output print level from the function.
    :type debug_level: Debug
    :return: list of vectors, one per facies. The vectors are normalised
             probabilities for the subset of grid cells defined by the
             cellIndexDefined index vector.
            TODO: Correct?
    """
    # The list probParamValuesForFacies has items =[name,values]
    # Define index names for this item
    NAME = 0
    VAL = 1

    # Check that probabilities sum to 1
    functionName = 'checkAndNormaliseProb'
    if debug_level >= Debug.VERY_VERBOSE:
        if not useConstProb:
            print('Debug output: Check normalisation of probability cubes.')
        else:
            print('Debug output: Check normalisation of probabilities.')

    probDefined = []
    nCellWithModifiedProb = 0
    if not useConstProb:
        # Allocate space for probability per facies per defined cell
        for f in range(nFacies):
            probDefined.append(np.zeros(nDefinedCells, np.float32))
            item = probParamValuesForFacies[f]
            fName = item[NAME]
            values = item[VAL]
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies: ' + fName)

            nNeg = 0
            nAboveOne = 0
            for i in range(nDefinedCells):
                indx = cellIndexDefined[i]
                v = values[indx]
                if v < 0.0:
                    nNeg += 1
                elif v > 1.0:
                    nAboveOne += 1
                probDefined[f][i] = v
            if nNeg > 0:
                raise ValueError('Probability for facies ' + fName + ' has ' + str(nNeg) + ' negative values')
            if nAboveOne > 0:
                raise ValueError('Probability for facies ' + fName + ' has ' + str(nAboveOne) + ' values above 1.0')

        # Sum up probability over all facies per defined cell
        psum = probDefined[0]
        ones = np.ones(nDefinedCells, np.float32)
        for f in range(1, nFacies):
            # sum of np arrays (cell by cell sum)
            psum += probDefined[f]

        if not np.allclose(psum, ones, eps):
            if debug_level >= Debug.VERBOSE:
                text = '--- Normalise probability cubes.'
                print(text)

            zeroProbSum = 0
            for i in range(nDefinedCells):
                if psum[i] < 10 * eps:
                    zeroProbSum += 1

            if zeroProbSum > 0:
                raise ValueError(
                    'Error: Sum of input facies probabilities is less than: {} in: {} cells.\n'
                    '       Cannot normalize probabilities. Check your input!'
                    ''.format(10 * eps, zeroProbSum)
                )
            for f in range(nFacies):
                p = probDefined[f]  # Points to array of probabilities
                for i in range(nDefinedCells):
                    if np.abs(psum[i] - 1.0) > eps:
                        # Have to normalize
                        if f == 0:
                            nCellWithModifiedProb += 1
                        p[i] = p[i] / psum[i]
                        # print('i,p,psum:' + str(i) + ' ' + str(p[i]) + ' ' + str(psum[i]))

            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Number of grid cells in zone is:             ' + str(nDefinedCells))
                print('Debug output: Number of grid cells that are normalised is: ' + str(nCellWithModifiedProb))
    else:
        for f in range(nFacies):
            item = probParamValuesForFacies[f]
            fName = item[NAME]
            values = item[VAL]
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Facies: ' + fName + ' with constant probability: ' + str(values[0]))
            probDefined.append(values[0])

        # Check that probabilities sum to 1
        psum = probDefined[0]
        for f in range(1, nFacies):
            psum = psum + probDefined[f]
        if abs(psum - 1.0) > eps:
            raise ValueError(
                'Probabilities for facies are not normalized for this zone '
                '(Total: {})'.format(str(psum))
            )

    return [probDefined, nCellWithModifiedProb]


def createTrend(trendModelObj, gridModel, realNumber, nDefinedCells,
                cellIndexDefined, zoneNumber, simBoxThickness, debug_level=Debug.OFF):
    if trendModelObj.type == 'Trend3D_linear':
        trendObj = Trend3D_linear.Trend3D_linear(trendModelObj, debug_level)
        [minmaxDifference, trendValues] = trendObj.createTrend(
            gridModel, realNumber, nDefinedCells, cellIndexDefined, zoneNumber, simBoxThickness
        )
    else:
        raise ValueError('Trend type: ' + trendModelObj.type + ' is not implemented.')
    return [minmaxDifference, trendValues]


# --------------- Start main script ------------------------------------------

realNumber = project.current_realisation
print('Run: APS_trunc  on realisation ' + str(realNumber + 1))

modelFileName = 'APS.xml'

print('- Read file: ' + modelFileName)
apsModel = APSModel.APSModel(modelFileName)
debug_level = apsModel.debug_level()
rmsProjectName = apsModel.getRMSProjectName()
gridModelName = apsModel.getGridModelName()
gridModel = project.grid_models[gridModelName]
if gridModel.is_empty():
    raise ValueError('Specified grid model: ' + gridModel.name + ' is empty.')

zoneNumberList = apsModel.getZoneNumberList()
zoneParamName = apsModel.getZoneParamName()
resultParamName = apsModel.getResultFaciesParamName()

gaussFieldScript = apsModel.getRMSGaussFieldScriptName()

# For testing
# apsModel.createSimGaussFieldIPL()

# Get zone param values
if debug_level >= Debug.VERBOSE:
    print('--- Get RMS zone parameter: ' + zoneParamName + ' from RMS project ' + rmsProjectName)
[zoneValues] = gr.getContinuous3DParameterValues(gridModel, zoneParamName, realNumber, debug_level)

emptyZoneList = []
# Find min max zone over all active cells, send an empty zone list which means that all zones are selected
(minZone, maxZone, avgzone) = gr.calcStatisticsFor3DParameter(
    gridModel, zoneParamName, emptyZoneList, realNumber, debug_level
)

# Allocate space for facies realisation and calculated volume fractions
nCellsTotal = len(zoneValues)
faciesReal = np.zeros(nCellsTotal, np.uint16)

# Gaussian field related lists
GFNamesAlreadyRead = []
GFAllValues = []
GFAllAlpha = []

# Probability related lists
probParamNamesAlreadyRead = []
probParamAllValues = []
# The four lists: probParamAllValues,probParamValuesForFacies,GFAllValues, GFAllAlpha
# will use a list of items where the item is of the form item =[name,value]
# Index values are defined by:
NAME = 0  # Name of index in items = [ name, values]
VAL = 1  # Name of index in items = [ name, values]

# List of modelled facies names
allFaciesNamesModelled = []
selectedZoneNumberList = apsModel.getSelectedZoneNumberList()
if debug_level >= Debug.VERY_VERBOSE:
    print('Debug output: Selected zone numbers to simulate:')
    print(repr(selectedZoneNumberList))
# Loop over all zones
# This loop calculates facies for each specified zone for main facies level
for zoneNumber in zoneNumberList:
    if not zoneNumber in selectedZoneNumberList:
        continue

    if debug_level >= Debug.SOMEWHAT_VERBOSE:
        print(' ')
        print('- Run model for zone number: ' + str(zoneNumber))
        print(' ')

    zoneModel = apsModel.getZoneModel(zoneNumber)
    # Read trend parameters for truncation parameters
    # zoneModel.getTruncationParam(gridModel,realNumber)
    zoneModel.getTruncationParam(gr.getContinuous3DParameterValues, gridModel, realNumber)

    useConstProb = zoneModel.useConstProb()
    GFNamesForZone = zoneModel.getUsedGaussFieldNames()
    faciesNamesForZone = zoneModel.getFaciesInZoneModel()
    nFacies = len(faciesNamesForZone)

    if debug_level >= Debug.VERBOSE:
        for gfName in GFNamesForZone:
            print('--- Gauss field parameter used for this zone: ' + gfName)

    # Get the gauss field parameter name if not already done.
    for gfName in GFNamesForZone:
        if not (gfName in GFNamesAlreadyRead):
            GFNamesAlreadyRead.append(gfName)
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Gauss field parameter: ' + gfName + ' is now being loaded.')
            [values] = gr.getContinuous3DParameterValues(gridModel, gfName, realNumber, debug_level)

            # Allocate space for transformed gauss field property vector alpha
            alpha = np.zeros(len(values), np.float32)

            GFAllValues.append([gfName, values])
            gfNameTrans = gfName + '_transf'
            GFAllAlpha.append([gfNameTrans, alpha])

        else:
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Gauss field parameter: ' + gfName + ' is already loaded.')

    # For current zone find the active cells for this zone 
    (nDefinedCells, cellIndexDefined) = findDefinedCells(zoneValues, zoneNumber, debug_level)
    if debug_level >= Debug.VERBOSE:
        print('--- Number of active cells for zone: ' + str(nDefinedCells))

    # For current zone,transform all gaussian fields used in this zone and update alpha 
    indx = -999
    GFAlphaForCurrentZone = []
    zList = [zoneNumber - 1]
    for gfName in GFNamesForZone:
        for j in range(len(GFAllValues)):
            gName = GFAllValues[j][NAME]
            if gName == gfName:
                indx = j
                break
        values = GFAllValues[indx][VAL]

        # Add trend to gaussian residual fields
        [useTrend, trendModelObj, relStdDev] = zoneModel.getTrendRuleModel(gfName)

        if useTrend == 1:
            simBoxThickness = zoneModel.getSimBoxThickness()
            # trendValues contain trend values for the cells belonging to the set defined by cellIndexDefined
            [minmaxDifference, trendValues] = createTrend(
                trendModelObj, gridModel, realNumber, nDefinedCells,
                cellIndexDefined, zoneNumber, simBoxThickness, debug_level
            )
            if debug_level >= Debug.VERBOSE:
                print('--- Calculate trend for: ' + gfName + ' for zone: ' + str(zoneNumber))

            sigma = relStdDev * minmaxDifference
            residualValues = values[cellIndexDefined]
            val = trendValues + sigma * residualValues
            values[cellIndexDefined] = val
            if debug_level >= Debug.VERY_VERBOSE:
                print('Debug output: Trend minmaxDifference = ' + str(minmaxDifference))
                print('Debug output: SimBoxThickness = ' + str(simBoxThickness))
                print('Debug output: RelStdDev = ' + str(relStdDev))
                print('Debug output: trendValues:')
                print(repr(trendValues))
                print(
                    'Debug output: Min trend, max trend    : ' + str(trendValues.min()) + ' ' + str(trendValues.max()))
                print('Debug output: Residual min,max        : ' + str(residualValues.min()) + ' ' + str(
                    residualValues.max()))
                print('Debug output: trend + residual min,max: ' + str(val.min()) + ' ' + str(val.max()))
                print('Debug output: Trend + Residual values:')
                print(repr(val))

        alpha = GFAllAlpha[indx][VAL]
        # Update alpha for current zone
        if debug_level >= Debug.VERBOSE:
            print('--- Transform: {} for zone: {}'.format(gfName, zoneNumber))
        alpha = transformEmpiric(nDefinedCells, cellIndexDefined, values, alpha)
        GFAllAlpha[indx][VAL] = alpha
        gfNamesTrans = GFAllAlpha[indx][NAME]

        # List of transformed values for each facies for current zone
        GFAlphaForCurrentZone.append([gfName, alpha])

        # Write back to RMS project the transformed gaussian values for the zone
        # Only current zone is updated
        if not gr.setContinuous3DParameterValues(gridModel, gfNamesTrans, alpha, zList, realNumber, False, debug_level):
            raise ValueError('Cannot create parameter {} in {}'.format(gfNamesTrans, gridModel.name))
        else:
            if debug_level >= Debug.VERBOSE:
                print('--- Create or update parameter: {} for zone number: {}'.format(gfNamesTrans, zoneNumber))

    # Get all facies names to be modelled for this zone and corresponding probability parameters
    probParamValuesForFacies = []
    for fName in faciesNamesForZone:
        probParamName = zoneModel.getProbParamName(fName)
        if debug_level >= Debug.VERY_VERBOSE:
            print('Debug output: Zone: {}  Facies name: {}  Probability: {}'.format(zoneNumber, fName, probParamName))
        values = []
        if useConstProb == 1:
            values.append(float(probParamName))
            # Add the probability values to a common list containing probabilities for
            # all facies used in the whole model (all zones) to avoid loading the same data multiple times.
            probParamAllValues.append([fName, values])

            # Probabilities for each facies for current zone
            probParamValuesForFacies.append([fName, values])
        else:
            if not (probParamName in probParamNamesAlreadyRead):
                probParamNamesAlreadyRead.append(probParamName)
                if debug_level >= Debug.VERY_VERBOSE:
                    print(
                        'Debug output: Probability parameter: {} is now being loaded for facies: {} for zone: {}'
                        ''.format(probParamName, fName, zoneNumber)
                    )

                [values] = gr.getContinuous3DParameterValues(gridModel, probParamName, realNumber, debug_level)

                # Add the probability values to a common list containing probabilities for
                # all facies used in the whole model (all zones) to avoid loading the same data multiple times.
                probParamAllValues.append([fName, values])

                # Probabilities for each facies for current zone
                probParamValuesForFacies.append([fName, values])

            else:
                if debug_level >= Debug.VERY_VERBOSE:
                    print(
                        'Debug output: Probability parameter: {} is already loaded for facies: {} for zone: {}'
                        ''.format(probParamName, fName, zoneNumber)
                    )

                indx = -999
                # Get the probability values from the common list since it already is loaded
                for i in range(len(probParamAllValues)):
                    fN = probParamAllValues[i][NAME]
                    if fName == fN:
                        indx = i
                        break
                # Probabilities for each facies for current zone
                values = probParamAllValues[indx][VAL]
                probParamValuesForFacies.append([fName, values])

    # end for

    # Check and normalise probabilities if necessary for current zone
    if debug_level >= Debug.VERBOSE:
        print('--- Check normalisation of probability fields.')
    [probDefined, nCellsModifiedProb] = checkAndNormaliseProb(
        nFacies, probParamValuesForFacies, useConstProb, nDefinedCells, cellIndexDefined, eps, debug_level
    )
    if debug_level >= Debug.VERBOSE:
        print('--- Number of cells that are normalised: ' + str(nCellsModifiedProb))

        # Facies realisation for current zone is updated.
        if debug_level >= Debug.VERBOSE:
            print('--- Truncate transformed Gaussian fields.')

    [faciesReal, volFrac] = zoneModel.applyTruncations(
        probDefined, GFAlphaForCurrentZone, faciesReal, nDefinedCells, cellIndexDefined
    )

    if debug_level >= Debug.VERBOSE:
        print(' ')
        mainFaciesTable = apsModel.getMainFaciesTable()
        if useConstProb == 1:
            print(
                '--- Zone_number:    Facies_code:   Facies_name:'
                '     Volumefraction_specified:    Volumefracion_realisation:'
            )
            for f in range(len(faciesNamesForZone)):
                fName = faciesNamesForZone[f]
                fCode = mainFaciesTable.getFaciesCodeForFaciesName(fName)
                item = probParamValuesForFacies[f]
                if fName != item[NAME]:
                    raise ValueError('Inconsistencies in data structure in APS_main')

                probValues = item[VAL]
                print('{0:4d} {1:4d}  {2:10}  {3:.3f}   {4:.3f}'.format(
                    zoneNumber, fCode, fName, probValues[0], volFrac[f])
                )

        else:
            print(
                '--- Zone_number:    Facies_code:   Facies_name:'
                '     Volumefraction_realisation  Volumefraction_from_probcube:'
            )
            for f in range(len(faciesNamesForZone)):
                fName = faciesNamesForZone[f]
                fCode = mainFaciesTable.getFaciesCodeForFaciesName(fName)
                item = probParamValuesForFacies[f]
                if fName != item[NAME]:
                    raise ValueError('Inconsistencies in data structure in APS_main')

                values = item[VAL]
                avgProbValue = gr.calcAverage(nDefinedCells, cellIndexDefined, values)
                print('{0:4d} {1:4d}  {2:10}  {3:.3f}   {4:.3f}'.format(zoneNumber, fCode, fName, volFrac[f],
                                                                        avgProbValue))

        for fName in faciesNamesForZone:
            # fCode = mainFaciesTable.getFaciesCodeForFaciesName(fName)
            if fName not in allFaciesNamesModelled:
                allFaciesNamesModelled.append(fName)
                if debug_level >= Debug.VERY_VERBOSE:
                    print('Debug: Add facies: ' + fName + ' to the list of modelled facies')

# End loop over zones

print(' ')

# Write/update facies realisation
mainFaciesTable = apsModel.getMainFaciesTable()
codeNames = {}
for i in range(len(allFaciesNamesModelled)):
    fName = allFaciesNamesModelled[i]
    fCode = mainFaciesTable.getFaciesCodeForFaciesName(fName)
    codeNames.update({fCode: fName})

if debug_level >= Debug.VERY_VERBOSE:
    text = 'Debug output: Facies codes and names before merging with existing facies table for facies realisation:'
    print(text)
    print(repr(codeNames))

# Write facies realisation back to RMS project for all zones that is modelled.

if debug_level >= Debug.VERBOSE:
    print('--- The following zone numbers are updated in facies realization:')
zList = []
for s in zoneNumberList:
    if s in selectedZoneNumberList:
        zList.append(s - 1)
        if debug_level >= Debug.VERBOSE:
            print('    Zone: ' + str(s))

gr.setDiscrete3DParameterValues(
    gridModel, resultParamName, faciesReal, zList, codeNames,
    realNumber, False, debug_level
)
if debug_level >= Debug.SOMEWHAT_VERBOSE:
    print('- Create or update parameter: ' + resultParamName)

print(' ')
if debug_level >= Debug.SOMEWHAT_VERBOSE:
    print('- Updated facies table:')
    p = gr.get3DParameter(gridModel, resultParamName, realNumber, debug_level)
    print('- Facies_name   Facies_code')
    for key in p.code_names:
        u = p.code_names.get(key)
        print('  {0:10}  {1:3d}'.format(u, key))

    print(' ')
print('Finished APS_main.py')
