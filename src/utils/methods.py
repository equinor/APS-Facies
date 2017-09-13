import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", newl="\n")


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
