from enum import Enum
import random
from typing import Iterable
from dataclasses import dataclass

from xml.etree.ElementTree import Element, ElementTree
import xml.etree.ElementTree as ET

from xsd2xml.types import (
    BuiltInType,
    ComplexType,
    SimpleType,
    random_build_in_type,
    random_string,
)
from xsd2xml.utils import CallerError, ns, InvalidXSDError


class XSD(str, Enum):
    element = "{http://www.w3.org/2001/XMLSchema}element"
    sequence = "{http://www.w3.org/2001/XMLSchema}sequence"
    choice = "{http://www.w3.org/2001/XMLSchema}choice"
    all = "{http://www.w3.org/2001/XMLSchema}all"
    any = "{http://www.w3.org/2001/XMLSchema}any"
    attribute = "{http://www.w3.org/2001/XMLSchema}attribute"
    anyAttribute = "{http://www.w3.org/2001/XMLSchema}anyAttribute"
    complex_type = "{http://www.w3.org/2001/XMLSchema}complexType"
    simple_type = "{http://www.w3.org/2001/XMLSchema}simpleType"
    simple_content = "{http://www.w3.org/2001/XMLSchema}simpleContent"
    complex_content = "{http://www.w3.org/2001/XMLSchema}complexContent"
    attribute_group = "{http://www.w3.org/2001/XMLSchema}attributeGroup"
    group = "{http://www.w3.org/2001/XMLSchema}group"
    list = "{http://www.w3.org/2001/XMLSchema}list"
    restriction = "{http://www.w3.org/2001/XMLSchema}restriction"
    extension = "{http://www.w3.org/2001/XMLSchema}extension"
    union = "{http://www.w3.org/2001/XMLSchema}union"
    enumeration = "{http://www.w3.org/2001/XMLSchema}enumeration"
    length = "{http://www.w3.org/2001/XMLSchema}length"

@dataclass
class Context:
    root: Element
    namespaces: dict[str, str]


def generate(xsd_path: str, element_name: str) -> ElementTree:
    xsd_tree = ET.parse(xsd_path)
    xsd_root = xsd_tree.getroot()

    if not isinstance(xsd_root, Element):
        raise ValueError()

    xsd_element = xsd_root.find(f"xsd:element[@name='{element_name}']", ns)
    if xsd_element is None:
        raise ValueError()

    created_element = _instantiate_element(xsd_root, xsd_element)
    created_element = next(iter(created_element))

    target_namespace = xsd_root.get("targetNamespace")
    if target_namespace is not None:
        created_element.attrib["xmlns"] = target_namespace

    return ElementTree(created_element)


def _try_resolve_reference(xsd_root: Element, element: Element) -> Element:
    ref = element.get("ref")
    tag = element.tag
    if ref is not None:
        referenced_element = xsd_root.find(f"{tag}[@name='{ref}']")
        if referenced_element is None:
            raise InvalidXSDError()
        return referenced_element

    return element


def _get_random_occurs(xsd_element: Element) -> int:
    min_occurs = xsd_element.get("minOccurs")
    min_occurs = min_occurs if min_occurs else 1

    max_occurs = xsd_element.get("maxOccurs")
    max_occurs = max_occurs if max_occurs else 1
    max_occurs = 5 if max_occurs == "unbounded" else max_occurs

    return random.randint(int(min_occurs), int(max_occurs))


def _find_type_definition(
    xsd_root: Element, xsd_element: Element
) -> SimpleType | ComplexType | BuiltInType:
    type = _get_attribute(xsd_element, "type")
    if type in BuiltInType:
        return BuiltInType(type)

    if type is None:
        inline_type_def = next(
            el for el in xsd_element if el in (XSD.complex_type, XSD.simple_type)
        )
        match inline_type_def.tag:
            case XSD.complex_type:
                return ComplexType(inline_type_def)
            case XSD.simple_type:
                return SimpleType(inline_type_def)
            case _:
                raise InvalidXSDError()

    simple_type = xsd_root.find(f"xsd:simpleType[@name='{type}']", ns)
    if simple_type is not None:
        return SimpleType(simple_type)

    complex_type = xsd_root.find(f"xsd:complexType[@name='{type}']", ns)
    if complex_type is not None:
        return ComplexType(complex_type)

    raise InvalidXSDError()


def _instantiate_element(xsd_root: Element, xsd_element: Element) -> list[Element]:
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


def _create_build_in_element(xsd_element: Element) -> Element:
    name = xsd_element.get("name")
    if name is None:
        raise InvalidXSDError()
    generated_element = Element(name)
    xsd_type = _get_attribute(xsd_element, "type")
    if xsd_type is None or xsd_type not in BuiltInType:
        raise CallerError()
    generated_element.text = random_build_in_type(BuiltInType(xsd_type))
    return generated_element


def _create_complex_element(
    xsd_root: Element, xsd_element: Element, complex_type: Element
) -> Element:
    element_name = xsd_element.get("name")
    if element_name is None:
        raise InvalidXSDError()

    main_child = next(
        el for el in complex_type if el.tag != XSD.attribute
    )

    
    match main_child.tag:
        case XSD.sequence | XSD.choice | XSD.all:
            created_element = Element(element_name)
            _set_attributes(
                xsd_root, created_element, (el for el in complex_type if el.tag == XSD.attribute)
            )

            children = _recurse_indicator(xsd_root, main_child)
            created_element.extend(children)
        case XSD.simple_content:
            created_element = Element(element_name)
            return _generate_simple_content(xsd_root, created_element, main_child)
        case XSD.complex_content:
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()

    return created_element


def _recurse_indicator(xsd_root: Element, indicator: Element) -> list[Element]:
    result: list[Element] = []
    match indicator.tag:
        case XSD.element:
            # Base condition
            return _instantiate_element(xsd_root, indicator)
        case XSD.any:
            return _create_any_element(indicator)
        case XSD.sequence:
            for child in indicator:
                result.extend(_recurse_indicator(xsd_root, child))
        case XSD.choice:
            choice = random.choice([el for el in indicator])
            result = _recurse_indicator(xsd_root, choice)
        case XSD.all:
            for child in indicator:
                result.extend(_recurse_indicator(xsd_root, child))
            random.shuffle(result)
        case _:
            raise NotImplementedError()

    return result


def _set_attributes(
    xsd_root: Element,
    created_element: Element,
    xsd_attribute_list: Iterable[Element],
) -> None:
    for xsd_attribute in xsd_attribute_list:
        xsd_attribute = _try_resolve_reference(xsd_root, xsd_attribute)

        if xsd_attribute.tag == XSD.attribute_group:
            xsd_attribute_group = _try_resolve_reference(xsd_root, xsd_attribute)
            _set_attributes(
                xsd_root, created_element, (el for el in xsd_attribute_group)
            )

        if xsd_attribute.tag == XSD.anyAttribute:
            raise NotImplementedError()

        name = _get_attribute(xsd_attribute, "name")
        type = _get_attribute(xsd_attribute, "type")

        required = xsd_attribute.get("use") == "required"

        if name is None:
            raise InvalidXSDError()

        do_not_create = random.random() > 0.5
        if not required and do_not_create:
            continue

        if type in BuiltInType:
            created_element.attrib[name] = random_build_in_type(BuiltInType(type))
            continue

        is_type_user_defined = type is not None and type not in BuiltInType
        if is_type_user_defined:
            raise NotImplementedError()

        is_type_anonymous = type is None
        if is_type_anonymous:
            simple_type = next(el for el in xsd_attribute if el.tag == XSD.simple_type)
            created_element.attrib[name] = _generate_simple_type(simple_type)
            continue


def _generate_simple_type(simple_type: Element) -> str:
    child = next(el for el in simple_type)

    match child.tag:
        case XSD.list:
            raise NotImplementedError()
        case XSD.union:
            raise NotImplementedError()
        case XSD.restriction:
            return _generate_restricted(child)
        case _:
            raise InvalidXSDError()


def _generate_restricted(restriction: Element) -> str:
    base = _get_attribute(restriction, "base")
    if base is None:
        raise InvalidXSDError()

    if base not in BuiltInType:
        raise NotImplementedError()

    # Assuming the enumerations are correct
    enumerations = [el for el in restriction if el.tag == XSD.enumeration]

    if len(enumerations) != 0:
        enum_choice = random.choice(enumerations)
        enum_value = enum_choice.get("value")
        if enum_value is None:
            raise InvalidXSDError()
        return enum_value

    base = BuiltInType(base)
    match base:
        case BuiltInType.string:
            raise NotImplementedError()
        case _:
            raise NotImplementedError()


def _generate_simple_content(
    xsd_root: Element, created_element: Element, simple_content: Element
) -> Element:
    restriction_or_extension = next(el for el in simple_content)
    base = _get_attribute(restriction_or_extension, "base")
    if base is None:
        raise InvalidXSDError()

    if base not in BuiltInType:
        raise NotImplementedError()
    base = BuiltInType(base)

    match restriction_or_extension.tag:
        case XSD.restriction:
            raise NotImplementedError()
        case XSD.extension:
            created_element.text = random_build_in_type(base)
            _set_attributes(
                xsd_root,
                created_element,
                (el for el in restriction_or_extension if el == XSD.attribute),
            )
            return created_element
        case _:
            raise InvalidXSDError()


def _expand_qname(qname: str | None, nsmap: dict[str | None, str]) -> str | None:
    if qname is None:
        return None
    if ":" not in qname:
        return qname
    if "{" == next(iter(qname), None):
        return None
    idx = qname.find(":")
    return "{" + nsmap[qname[:idx]] + "}" + qname[idx + 1 :]


def _get_attribute(element: Element, attribute_name: str) -> str | None:
    attribute_value = element.get(attribute_name)
    # TODO
    # return _expand_qname(attribute_value, element.nsmap)
    return attribute_value



def _create_any_element(xsd_any: Element) -> list[Element]:
    # TODO: add something with a namespace
    random_occurs = _get_random_occurs(xsd_any)
    return [Element(random_string()) for _ in range(random_occurs)]
