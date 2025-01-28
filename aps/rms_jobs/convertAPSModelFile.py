import xml.etree.ElementTree as ET
from aps.utils.xmlUtils import prettify

def write(file_name: str, content: str) -> None:
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)

def run():
    input_model_file = "APS.xml"
    output_model_file = "APS_v1.0.xml"

    # Read APS model file with reader for version 1.0
    # It will then convert the input to 1.0 version which means that it will
    # ignore JobSettings keyword and use default values for JobSettings.
    # It is sufficient to just replace 1.1 with 1.0 for keyword APSModel.

    root = ET.parse(input_model_file).getroot()
    value = root.get('version')
    print(f'Input file: {input_model_file} has APS model file version: {value} ')

    key = 'version'
    value = '1.0'
    root.set(key,value)
    element_jobsettings = root.find('JobSettings')
    if element_jobsettings is not None:
        root.remove(element_jobsettings)
    print(f'Output file: {output_model_file} has APS model file version: {value} ')
    write(output_model_file, prettify(root, indent="",new_line=""))


if __name__ == "__main__":
    run()
