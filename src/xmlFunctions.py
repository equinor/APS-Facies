#!/bin/env python
import copy


def getKeyword(parent, keyword, parentKeyword='', modelFile=None, required=True):
    """ Read keyword and return the reference to the xml object for the keyword. 
        If keyword is not found, either error message is written if the keyword is required 
        or None is returned if the keyword is not required. 
        
    """
    obj = parent.find(keyword)
    if required:
        if obj is None:
            raise ValueError(
                'Missing keyword {} under keyword {} in model file {}'
                ''.format(keyword, parentKeyword, modelFile)
            )

    return obj


def getTextCommand(parent, keyword, parentKeyword='', defaultText=None, modelFile=None, required=True):
    """ Return the text string specified in the keyword. If the keyword is required,
        but the keyword does not exist, error message is called. 
        If the keyword is not required and the keyword is not found, the default text is returned.
    """
    obj = parent.find(keyword)
    text = copy.copy(defaultText)
    if required:
        if obj is None:
            raise ValueError(
                'Missing keyword {} under keyword {} in model file {}'
                ''.format(keyword, parentKeyword, modelFile)
            )
    if obj is not None:
        text = obj.text

    return text.strip()


def getFloatCommand(
        parent, keyword, parentKeyword='', minValue=None, maxValue=None,
        defaultValue=None, modelFile=None, required=True):
    """ Return the float value specified in the keyword. If the keyword is required,
        but the keyword does not exist, error message is called. 
        If the keyword is not required and the keyword is not found, the default value is returned.
        If minValue and/or maxValue is specified, the value read is checked against these.
        Error message is called if the value <= minValue or value >= maxValue. 
        Ensure that default value is set if the command is not required. 
    """

    obj = parent.find(keyword)
    value = defaultValue
    if required:
        if obj is None:
            raise ValueError(
                'Missing keyword {} under keyword {} in model file {}'
                ''.format(keyword, parentKeyword, modelFile)
            )
    if obj is not None:
        text = obj.text
        value = float(text.strip())
        if minValue is not None:
            if value < minValue:
                raise ValueError(
                    'Value specified in keyword {} under keyword {} in model file {} '
                    'is less than mininum value {}.'
                    ''.format(keyword, parentKeyword, modelFile, str(minValue))
                )
        if maxValue is not None:
            if value > maxValue:
                raise ValueError(
                    'Value specified in keyword {} under keyword {} in model file {} '
                    'is greater than maximum value {}.'
                    ''.format(keyword, parentKeyword, modelFile, str(maxValue))
                )

    return value


def getIntCommand(
        parent, keyword, parentKeyword='', minValue=None,
        maxValue=None, defaultValue=None, modelFile=None, required=True):
    """ Return the int value specified in the keyword. If the keyword is required,
        but the keyword does not exist, error message is called. 
        If the keyword is not required and the keyword is not found, the default value is returned.
        If minValue and/or maxValue is specified, the value read is checked against these.
        Error message is called if the value <= minValue or value >= maxValue. 
        Ensure that default value is set if the command is not required. 
    """
    obj = parent.find(keyword)
    value = defaultValue
    if required:
        if obj is None:
            raise ValueError(
                'Missing keyword {} under keyword {} in model file {}'
                ''.format(keyword, parentKeyword, modelFile)
            )
    if obj is not None:
        text = obj.text
        value = int(text.strip())
        if minValue is not None:
            if value < minValue:
                raise ValueError(
                    'Value specified in keyword {} under keyword {} in model file {} '
                    'is less than mininum value {}.'
                    ''.format(keyword, parentKeyword, modelFile, str(minValue))
                )
        if maxValue is not None:
            if value > maxValue:
                raise ValueError(
                    'Value specified in keyword {} under keyword {} in model file {} '
                    'is greater than maximum value {}.'
                    ''.format(keyword, parentKeyword, modelFile, str(maxValue))
                )

    return value
