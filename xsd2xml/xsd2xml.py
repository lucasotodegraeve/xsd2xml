import xml.etree.ElementTree as ET

from .core.etree import _ElementTree
from .core import idrefs, element
from .core.namespaces import xsd


def generate(xsd_path: str, element_name: str) -> ET.ElementTree:
    xsd_tree = _ElementTree.parse(xsd_path)
    xsd_root = xsd_tree.getroot()

    xsd_element = xsd_root.find(f"{xsd.element}[@name='{element_name}']")
    if xsd_element is None:
        raise ValueError()

    ph_elements = element.generate_element(xsd_element)
    ph_element = next(iter(ph_elements))
    root_element = ph_element.manifest_placeholders()

    idrefs._recurse_markers(root_element)

    return ET.ElementTree(root_element)
