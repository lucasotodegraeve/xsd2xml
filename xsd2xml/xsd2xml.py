import xml.etree.ElementTree as ET

from xsd2xml.core.etree import _ElementTree
from xsd2xml.core import idrefs, element


def generate(xsd_path: str, element_name: str) -> ET.ElementTree:
    xsd_tree = _ElementTree.parse(xsd_path)
    xsd_root = xsd_tree.getroot()

    xsd_element = xsd_root.find(f"xsd:element[@name='{element_name}']")
    if xsd_element is None:
        raise ValueError()

    # TODO: check if there are ids if idrefs are required

    created_element = element._recursively_generate_element(xsd_element)
    created_element = next(iter(created_element))
    created_element = created_element._recurse_to_element()

    idrefs._recurse_markers(created_element)

    target_namespace = xsd_root.get("targetNamespace")
    if target_namespace is not None:
        created_element.attrib["xmlns"] = target_namespace

    return ET.ElementTree(created_element)
