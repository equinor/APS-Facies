# -*- coding: utf-8 -*-
from xml.dom import minidom
from xml.etree import ElementTree as ET

from src.utils.exceptions.xml import ReadingXmlError, LessThanExpected, MoreThanExpected


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", newl="\n")


def getKeyword(parent, keyword, parentKeyword='', modelFile=None, required=True):
    """
    Read keyword and return the reference to the xml object for the keyword.
    If keyword is not found, either error message is written if the keyword is required
    or None is returned if the keyword is not required.
    """
    obj = parent.find(keyword)
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    return obj


def getTextCommand(parent, keyword, parentKeyword='', defaultText=None, modelFile=None, required=True):
    """
    Return the text string specified in the keyword. If the keyword is required,
    but the keyword does not exist, error message is called.
    If the keyword is not required and the keyword is not found, the default text is returned.
    """
    obj = parent.find(keyword)
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    if obj is not None:
        text = obj.text.strip()
    else:
        text = defaultText

    return text


def getFloatCommand(
        parent, keyword, parentKeyword='', minValue=None, maxValue=None,
        defaultValue=None, modelFile=None, required=True
):
    """
    Return the float value specified in the keyword. If the keyword is required,
    but the keyword does not exist, error message is called.
    If the keyword is not required and the keyword is not found, the default value is returned.
    If minValue and/or maxValue is specified, the value read is checked against these.
    Error message is called if the value <= minValue or value >= maxValue.
    Ensure that default value is set if the command is not required.
    """

    obj = parent.find(keyword)
    value = defaultValue
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    if obj is not None:
        text = obj.text
        value = float(text.strip())
        if minValue is not None and value < minValue:
            raise LessThanExpected(keyword, value, minValue, parentKeyword, modelFile)
        if maxValue is not None and value > maxValue:
            raise MoreThanExpected(keyword, value, maxValue, parentKeyword, modelFile)
    return value


def getIntCommand(
        parent, keyword, parentKeyword='', minValue=None,
        maxValue=None, defaultValue=None, modelFile=None, required=True
):
    """
    Return the int value specified in the keyword. If the keyword is required,
    but the keyword does not exist, error message is called.
    If the keyword is not required and the keyword is not found, the default value is returned.
    If minValue and/or maxValue is specified, the value read is checked against these.
    Error message is called if the value <= minValue or value >= maxValue.
    Ensure that default value is set if the command is not required.
    """
    obj = parent.find(keyword)
    value = defaultValue
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    if obj is not None:
        text = obj.text
        value = int(text.strip())
        if minValue is not None and value < minValue:
            raise LessThanExpected(keyword, value, minValue, parentKeyword, modelFile)
        if maxValue is not None and value > maxValue:
            raise MoreThanExpected(keyword, value, maxValue, parentKeyword, modelFile)
    return value


def getBoolCommand(parent, keyword, parent_keyword='', default=False, model_file_name=None, required=True):
    obj = parent.find(keyword)
    value = default
    if required and obj is None:
        raise ReadingXmlError(keyword, parent_keyword, model_file_name)
    if obj is not None:
        text = obj.text.strip().lower()
        if text in ['true', '1', 'yes', 'y']:
            value = True
        elif text in ['false', '0']:
            value = False
        else:
            raise ReadingXmlError(keyword, parent_keyword, model_file_name)
    return value