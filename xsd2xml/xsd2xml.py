from enum import Enum
import typing
import random

from lxml import etree
from lxml.etree import _Element, _ElementTree  # type: ignore

from xsd2xml.types import BuiltInType, generate_build_in_type  # type: ignore
from xsd2xml.utils import ns, InvalidXSDError


class XSD(str, Enum):
    element = "{http://www.w3.org/2001/XMLSchema}element"
    sequence = "{http://www.w3.org/2001/XMLSchema}sequence"
    choice = "{http://www.w3.org/2001/XMLSchema}choice"
    all = "{http://www.w3.org/2001/XMLSchema}all"
    attribute = "{http://www.w3.org/2001/XMLSchema}attribute"
    complex_type = "{http://www.w3.org/2001/XMLSchema}complexType"
    simple_type = "{http://www.w3.org/2001/XMLSchema}simpleType"
    # simple_content
    # complex_content
    # attribute_group
    # element_group


def generate(xsd_path: str, element_name: str) -> _ElementTree:
    xsd_tree = etree.parse(xsd_path)
    xsd_root = xsd_tree.getroot()
    xsd_element = xsd_root.find(f"xsd:element[@name='{element_name}']", namespaces=ns)
    if xsd_element is None:
        raise ValueError()

    instantiated_element = _instantiate_element(xsd_root, xsd_element)
    return etree.ElementTree(next(iter(instantiated_element)))


def _instantiate_element(
    xsd_root: _Element, element_to_instantiate: _Element
) -> list[_Element]:
    min_occurs = element_to_instantiate.get("minOccurs")
    min_occurs = min_occurs if min_occurs else 1

    max_occurs = element_to_instantiate.get("maxOccurs")
    max_occurs = max_occurs if max_occurs else 1
    max_occurs = 5 if max_occurs == "unbounded" else max_occurs

    random_occurs = random.randint(int(min_occurs), int(max_occurs))

    ref = element_to_instantiate.get("ref")
    if ref is not None:
        ref_element = xsd_root.find(f"xsd:element[@name='{ref}']", namespaces=ns)
        if ref_element is None:
            raise InvalidXSDError()
        element_to_instantiate = ref_element

    name = element_to_instantiate.get("name")
    if name is None:
        raise InvalidXSDError()

    result: list[_Element] = []
    type = element_to_instantiate.get("type")
    if type in BuiltInType:
        for _ in range(random_occurs):
            curr_element = etree.Element(name)
            _populate_build_in_element(curr_element, typing.cast(BuiltInType, type))
            result.append(curr_element)
        return result

    if type is None:
        inline_types = list(
            element_to_instantiate.iterchildren(XSD.complex_type, XSD.simple_type)
        )
        if len(inline_types) != 1:
            raise InvalidXSDError()
        xsd_type_element = inline_types[0]
    else:
        simple_type = xsd_root.find(f"xsd:simpleType[@name='{type}']", namespaces=ns)
        complex_type = xsd_root.find(f"xsd:complexType[@name='{type}']", namespaces=ns)
        if simple_type is None and complex_type is None:
            raise InvalidXSDError()
        xsd_type_element = typing.cast(_Element, simple_type or complex_type)

    for _ in range(random_occurs):
        curr_element = etree.Element(name)
        _populate_element(xsd_root, curr_element, xsd_type_element)
        result.append(curr_element)
    return result


def _populate_element(
    xsd_root: _Element, curr_element: _Element, type_to_instantiate: _Element
):
    match type_to_instantiate.tag:
        case XSD.complex_type:
            _populate_complex_type(xsd_root, curr_element, type_to_instantiate)
            return curr_element
        case XSD.simple_type:
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()


def _populate_build_in_element(element: _Element, type: BuiltInType) -> None:
    element.text = generate_build_in_type(type)


def _populate_complex_type(
    xsd_root: _Element, curr_element: _Element, complex_type: _Element
) -> None:
    for child_of_complex in complex_type.iterchildren():
        match child_of_complex.tag:
            case XSD.attribute:
                _populate_attribute(curr_element, child_of_complex)
            case XSD.sequence | XSD.choice | XSD.all:
                result = _generate_indicator(xsd_root, child_of_complex)
                curr_element.extend(result)
            case _:
                raise NotImplementedError()


def _generate_indicator(xsd_root: _Element, indicator: _Element) -> list[_Element]:
    result: list[_Element] = []
    match indicator.tag:
        case XSD.element:
            # Base condition
            return _instantiate_element(xsd_root, indicator)
        case XSD.sequence:
            for child in indicator.iterchildren():
                result.extend(_generate_indicator(xsd_root, child))
        case XSD.choice:
            choice = random.choice(list(indicator.iterchildren()))
            result = _generate_indicator(xsd_root, choice)
        case XSD.all:
            for child in indicator.iterchildren():
                result.extend(_generate_indicator(xsd_root, child))
            random.shuffle(result)
        case _:
            raise NotImplementedError()

    return result


def _populate_attribute(curr_element: _Element, attribute_element: _Element) -> None:
    name = attribute_element.get("name")
    type = attribute_element.get("type")

    if type not in BuiltInType:
        # TODO: could also be a simple type
        raise InvalidXSDError("Attribute must have a simple type")
    if name is None:
        raise InvalidXSDError("Attribute must have attrubute @name")

    value = generate_build_in_type(typing.cast(BuiltInType, type))
    curr_element.set(name, value)
