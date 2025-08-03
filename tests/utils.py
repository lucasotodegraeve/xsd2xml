import io
import xml.etree.ElementTree as ET
import random
import re

from xsd2xml.core.etree import _Element
from xsd2xml.core import helpers, types
from xsd2xml.core.namespaces import xsd
from xsd2xml.core import builtins, element
from xsd2xml.core.utils import InvalidXSDError


def seed_range(n: int):
    for i in range(n):
        set_seed(i)
        yield i


def set_seed(i: int):
    random.seed(i)


def serialize_tree(tree: ET.ElementTree) -> str:
    data = io.StringIO()
    ET.indent(tree)
    tree.write(data, encoding="unicode")
    return data.getvalue()


def check_generated_tree_coverage(document: ET.ElementTree, xsd_schema: ET.ElementTree):
    xsd_root = xsd_schema.getroot()
    document_root = document.getroot()

    if document_root is None or xsd_root is None:
        raise Exception()

    occurences = count_content_occurences(document_root)

    xsd_root = _Element(xsd_root, root=xsd_root)

    root_name = document_root.tag
    match = re.match(r"{.*}(\w+)", root_name)
    if not match:
        raise Exception()
    root_local_name = match.group(1)

    xsd_element = xsd_root.find(f"{xsd.element}[@name='{root_local_name}']")
    if xsd_element is None:
        raise Exception()


def calculate_element_occurence_probability(xsd_element: _Element) -> dict[str, float]:
    xsd_element = helpers._try_resolve_reference(xsd_element)
    type_definition = types._find_type_definition_for_element(xsd_element)
    element_name = xsd_element.get("name")

    if element_name is None:
        raise InvalidXSDError()

    if isinstance(type_definition, builtins.BuiltIn):
        return {element_name: 1}


def count_content_occurences(element: ET.Element) -> dict[str, float]:
    occurences = {}

    for k in element.attrib.keys():
        attribute_path = "@" + k
        if attribute_path not in occurences:
            occurences[attribute_path] = 0
        occurences[attribute_path] += 1

    for child in element:
        child_occurences = count_content_occurences(child)
        child_occurences = prepend_tag_to_occurences(element, child_occurences)
        occurences |= child_occurences

    return occurences


def prepend_tag_to_occurences(
    element: ET.Element, occurences: dict[str, float]
) -> dict[str, float]:
    with_prepend = {}
    for k, v in occurences.items():
        with_prepend[element.tag + "/" + k] = v
    return with_prepend


def merge_occurences(
    first: dict[str, float], second: dict[str, float]
) -> dict[str, float]:
    result = first.copy()
    for k, v in second.items():
        if k not in result:
            result[k] = 0
        result[k] += v
    return result


def combine_breadcrumbs_to_element_path(breadcrumbs: list[ET.Element], tag: str) -> str:
    parent_path = "/".join([element.tag for element in breadcrumbs])
    return parent_path + "/" + tag


def combine_breadcrumbs_to_attribute_path(
    breadcrumbs: list[ET.Element], attribute: str
) -> str:
    parent_path = "/".join([element.tag for element in breadcrumbs])
    return parent_path + "/@" + attribute
