import xsd2xml
import xml.etree.ElementTree as ET

ET.register_namespace("premis", "http://www.loc.gov/premis/v3")

xml_document = xsd2xml.generate("tests/assets/premis.xsd.xml", "premis")

ET.indent(xml_document)
xml_document.write("premis.xml")
