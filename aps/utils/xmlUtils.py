#!/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
from typing import Optional, Union, Tuple, Any, Callable, List
from xml.dom import minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from aps.utils.exceptions.xml import ReadingXmlError, LessThanExpected, MoreThanExpected, MissingRequiredValue
from aps.utils.constants.simple import OriginType
from aps.utils.containers import FmuAttribute
from aps.utils.types import GaussianFieldName


def prettify(
        elem: Union[Element, str],
        indent: str = "  ",
        new_line: str = "\n"
) -> str:
    if isinstance(elem, str):
        rough_string = elem
    else:
        rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent=indent, newl=new_line)


def minify(elem: Element) -> str:
    return prettify(elem, indent="", new_line="")


def get_fmu_value_from_xml(xml_tree: Element, keyword: str, _type: type = float, **kwargs) -> Tuple[float, bool]:
    types = {
        float: getFloatCommand,
        int: getIntCommand,
    }
    value = types[_type](xml_tree, keyword, **kwargs)
    fmu_updatable = isFMUUpdatable(xml_tree, keyword)
    return value, fmu_updatable


def get_origin_type_from_model_file(trend_rule_xml: Element, model_file_name: str) -> OriginType:
    origin_type = getTextCommand(
        trend_rule_xml, 'origintype', modelFile=model_file_name, required=False, defaultText="Relative"
    )
    origin_type = origin_type.strip('\"\'')
    if origin_type.lower() == 'relative':
        return OriginType.RELATIVE
    elif origin_type.lower() == 'absolute':
        return OriginType.ABSOLUTE
    else:
        raise ValueError('Error: Origin type must be Relative or Absolute.')


def getKeyword(
        parent: Element,
        keyword: str,
        parentKeyword: str = '',
        modelFile: Optional[str] = None,
        required: bool = True
) -> Optional[Element]:
    """
    Read keyword and return the reference to the xml object for the keyword.
    If keyword is not found, either error message is written if the keyword is required
    or None is returned if the keyword is not required.
    """
    obj = parent.find(keyword)
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    return obj


def getTextCommand(
        parent: Element,
        keyword: str,
        parentKeyword: str = '',
        defaultText: Optional[str] = None,
        modelFile: Optional[str] = None,
        required: bool = True
) -> Optional[str]:
    """
    Return the text string specified in the keyword. If the keyword is required,
    but the keyword does not exist, error message is called.
    If the text string specified in the keyword is None but a value is required, 
    error message is called.
    If the keyword is not required and the keyword is not found, the default text is returned.
    """
    obj = parent.find(keyword)
    if required:
        if obj is None:
            raise ReadingXmlError(keyword, parentKeyword, modelFile)
        if obj.text is None:
            raise MissingRequiredValue(keyword, parentKeyword, modelFile)

    text = defaultText
    if obj is not None:
        if obj.text is not None:
            text = obj.text.strip()

    return text


def getFloatCommand(
        parent: Element,
        keyword: str,
        parentKeyword: str = '',
        minValue: Optional[float] = None,
        maxValue: Optional[float] = None,
        defaultValue: Optional[Union[int, float]] = None,
        modelFile: Optional[str] = None,
        required: bool = True,
        moduloAngle: Optional[float] = None,
) -> Optional[float]:
    """
    Return the float value specified in the keyword. If the keyword is required,
    but the keyword does not exist, error message is called.
    If the keyword is not required and the keyword is not found, the default value is returned.
    If minValue and/or maxValue is specified, the value read is checked against these.
    Error message is called if the value <= minValue or value >= maxValue.
    If moduloAngle is defined (and a postive number is required), the input value is regarded
    as an angle taking values in interval 0 to moduloAngle degrees.
    Ensure that default value is set if the command is not required.
    """

    obj = parent.find(keyword)
    value = defaultValue
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    if obj is not None:
        text = obj.text
        if text is None:
            if required:
                raise MissingRequiredValue(keyword, parentKeyword, modelFile)
            return None
        value = float(text.strip())
        if minValue is not None and minValue != NotImplemented and value < minValue:
            raise LessThanExpected(keyword, value, minValue, parentKeyword, modelFile)
        if maxValue is not None and maxValue != NotImplemented and value > maxValue:
            raise MoreThanExpected(keyword, value, maxValue, parentKeyword, modelFile)
        if moduloAngle is not None and moduloAngle != NotImplemented:
            if moduloAngle > 0:
                value = value % moduloAngle
                if value < 0.0:
                    value = value + moduloAngle
            else:
                raise ValueError('Modulo angle must be positive')
    return value


def getIntCommand(
        parent: Element,
        keyword: str,
        parentKeyword: str = '',
        minValue: Optional[int] = None,
        maxValue: Optional[int] = None,
        defaultValue: Optional[int] = None,
        modelFile: Optional[str] = None,
        required: bool = True,
        moduloAngle: Optional[float] = None,
) -> int:
    """
    Return the int value specified in the keyword. If the keyword is required,
    but the keyword does not exist, error message is called.
    If the keyword is not required and the keyword is not found, the default value is returned.
    If minValue and/or maxValue is specified, the value read is checked against these.
    Error message is called if the value <= minValue or value >= maxValue.
    If moduloAngle is defined (and a postive number is required), the input value is regarded
    as an angle taking values in interval 0 to moduloAngle degrees.
    Ensure that default value is set if the command is not required.
    """
    obj = parent.find(keyword)
    value = defaultValue
    if required and obj is None:
        raise ReadingXmlError(keyword, parentKeyword, modelFile)
    if obj is not None:
        text = obj.text
        value = int(text.strip())
        if minValue is not None and minValue != NotImplemented and value < minValue:
            raise LessThanExpected(keyword, value, minValue, parentKeyword, modelFile)
        if maxValue is not None and maxValue != NotImplemented and value > maxValue:
            raise MoreThanExpected(keyword, value, maxValue, parentKeyword, modelFile)
        if moduloAngle is not None and moduloAngle != NotImplemented:
            if moduloAngle > 0:
                value = value % moduloAngle
                if value < 0.0:
                    value = value + moduloAngle
            else:
                raise ValueError('Modulo angle must be positive')
    return value


def getBoolCommand(
        parent: Element,
        keyword: str,
        parent_keyword: str = '',
        default: bool = False,
        model_file_name: Optional[str] = None,
        required: bool = True
) -> bool:
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


def isFMUUpdatable(
        parent: Element,
        keyword: str
) -> bool:
    obj = parent.find(keyword)
    if obj is not None:
        kwAttribute = obj.get('kw')
        if kwAttribute is not None:
            return True
    return False


def fmu_xml_element(
        tag: str,
        value: Any,
        updatable: bool,
        zone_number: int,
        region_number: int,
        gf_name: GaussianFieldName,
        fmu_creator: Callable[[str, str, int, int], str],
        fmu_attributes: List[FmuAttribute],
) -> Element:
    obj = Element(tag)
    obj.text = f' {value} '
    if updatable:
        fmu_attribute = fmu_creator(tag, gf_name, zone_number, region_number)
        fmu_attributes.append(FmuAttribute(fmu_attribute, value))
        obj.attrib = dict(kw=fmu_attribute)
    return obj


def get_region_number(zone: Element) -> int:
    region_number = zone.get('regionNumber')
    if region_number is not None:
        region_number = int(region_number)
        if region_number < 0:
            raise ValueError(
                f'Region number must be positive integer if region is used.\n'
                f'Zero as region number means that regions is not used for the zone.\n'
                f'Can not have negative region number: {region_number}'
            )
    else:
        region_number = 0
    return region_number


def _coerce_none_to_integers(func):
    @wraps(func)
    def wrapper(*args):
        coerced = [arg if arg is not None else 0 for arg in args]
        return func(*coerced)

    return wrapper


@_coerce_none_to_integers
def createFMUvariableNameForTrend(
        keyword: str,
        grf_name: str,
        zone_number: int,
        region_number: Optional[int] = None,
) -> str:
    return f'APS_{zone_number}_{region_number}_GF_{grf_name}_TREND_{keyword.upper()}'


@_coerce_none_to_integers
def createFMUvariableNameForResidual(
        keyword: str,
        grf_name: str,
        zone_number: int,
        region_number: Optional[int] = None,
) -> str:
    return f'APS_{zone_number}_{region_number}_GF_{grf_name}_RESIDUAL_{keyword.upper()}'


@_coerce_none_to_integers
def createFMUvariableNameForBayfillTruncation(
        keyword: str,
        zone_number: int,
        region_number: Optional[int] = None,
) -> str:
    return f'APS_{zone_number}_{region_number}_TRUNC_BAYFILL_{keyword.upper()}'


@_coerce_none_to_integers
def createFMUvariableNameForNonCubicTruncation(
        index: int,
        zone_number: int,
        region_number: Optional[int] = None,
) -> str:
    return f'APS_{zone_number}_{region_number}_TRUNC_NONCUBIC_POLYNUMBER_{index}_ANGLE'

def create_node(tag: str, text: Optional[Union[str, float, int]] = None) -> ET.Element:
    element = ET.Element(tag)
    if text is not None:
        element.text = str(text)
    return element
