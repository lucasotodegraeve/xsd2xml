from enum import Enum
import random

from lxml import etree
from lxml.etree import _Element, _ElementTree  # type: ignore

from xsd2xml.types import BuiltInType, ComplexType, SimpleType, random_build_in_type
from xsd2xml.utils import CallerError, ns, InvalidXSDError


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

    created_element = _instantiate_element(xsd_root, xsd_element)
    return etree.ElementTree(next(iter(created_element)))


def _try_resolve_reference(xsd_root: _Element, xsd_element: _Element) -> _Element:
    ref = xsd_element.get("ref")
    if ref is not None:
        ref_element = xsd_root.find(f"xsd:element[@name='{ref}']", namespaces=ns)
        if ref_element is None:
            raise InvalidXSDError()
        return ref_element

    return xsd_element


def _get_random_occurs(xsd_element: _Element) -> int:
    min_occurs = xsd_element.get("minOccurs")
    min_occurs = min_occurs if min_occurs else 1

    max_occurs = xsd_element.get("maxOccurs")
    max_occurs = max_occurs if max_occurs else 1
    max_occurs = 5 if max_occurs == "unbounded" else max_occurs

    return random.randint(int(min_occurs), int(max_occurs))


def _find_type_definition(
    xsd_root: _Element, xsd_element: _Element
) -> SimpleType | ComplexType | BuiltInType:
    type = xsd_element.get("type")
    if type in BuiltInType:
        return BuiltInType(type)

    if type is None:
        inline_type_def = next(
            xsd_element.iterchildren(XSD.complex_type, XSD.simple_type)
        )
        match inline_type_def.tag:
            case XSD.complex_type:
                return ComplexType(inline_type_def)
            case XSD.simple_type:
                return SimpleType(inline_type_def)
            case _:
                raise InvalidXSDError()

    simple_type = xsd_root.find(f"xsd:simpleType[@name='{type}']", namespaces=ns)
    if simple_type is not None:
        return SimpleType(simple_type)

    complex_type = xsd_root.find(f"xsd:complexType[@name='{type}']", namespaces=ns)
    if complex_type is not None:
        return ComplexType(complex_type)

    raise InvalidXSDError()


def _instantiate_element(xsd_root: _Element, xsd_element: _Element) -> list[_Element]:
    xsd_element = _try_resolve_reference(xsd_root, xsd_element)
    random_occurs = _get_random_occurs(xsd_element)
    type_definition = _find_type_definition(xsd_root, xsd_element)

    match type_definition:
        case BuiltInType():
            return [_create_build_in_element(xsd_element) for _ in range(random_occurs)]
        case SimpleType():
            raise NotImplementedError()
        case ComplexType():
            return [
                _create_complex_element(xsd_root, xsd_element, type_definition.root)
                for _ in range(random_occurs)
            ]


def _create_build_in_element(xsd_element: _Element) -> _Element:
    name = xsd_element.get("name")
    if name is None:
        raise InvalidXSDError()
    generated_element = etree.Element(name)
    xsd_type = xsd_element.get("type")
    if xsd_type is None or xsd_type not in BuiltInType:
        raise CallerError()
    generated_element.text = random_build_in_type(BuiltInType(xsd_type))
    return generated_element


def _create_complex_element(
    xsd_root: _Element, xsd_element: _Element, complex_type: _Element
) -> _Element:
    element_name = xsd_element.get("name")
    if element_name is None:
        raise InvalidXSDError()

    created_element = etree.Element(element_name)

    for attribute_definition in complex_type.iterchildren(XSD.attribute):
        name, value = _create_attribute(attribute_definition)
        created_element.attrib[name] = value

    indicator = next(complex_type.iterchildren(XSD.sequence, XSD.choice, XSD.all))
    children = _recurse_indicator(xsd_root, indicator)
    created_element.extend(children)

    return created_element


def _recurse_indicator(xsd_root: _Element, indicator: _Element) -> list[_Element]:
    result: list[_Element] = []
    match indicator.tag:
        case XSD.element:
            # Base condition
            return _instantiate_element(xsd_root, indicator)
        case XSD.sequence:
            for child in indicator.iterchildren():
                result.extend(_recurse_indicator(xsd_root, child))
        case XSD.choice:
            choice = random.choice(list(indicator.iterchildren()))
            result = _recurse_indicator(xsd_root, choice)
        case XSD.all:
            for child in indicator.iterchildren():
                result.extend(_recurse_indicator(xsd_root, child))
            random.shuffle(result)
        case _:
            raise NotImplementedError()

    return result


def _create_attribute(attribute_definition: _Element) -> tuple[str, str]:
    name = attribute_definition.get("name")
    type = attribute_definition.get("type")

    if name is None:
        raise InvalidXSDError()

    if type in BuiltInType:
        return name, random_build_in_type(BuiltInType(type))

    # Simple type
    raise NotImplementedError()
