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

    # TODO: attribute is not allowed for simple content (and complex content)?
    for attribute_definition in complex_type.iterchildren(XSD.attribute):
        _set_attribute(created_element, attribute_definition)

    main_child = next(
        filter(lambda el: el.tag != XSD.attribute, complex_type.iterchildren())
    )

    match main_child.tag:
        case XSD.sequence | XSD.choice | XSD.all:
            children = _recurse_indicator(xsd_root, main_child)
            created_element.extend(children)
        case XSD.simple_content:
            _generate_simple_content(main_child)
            raise NotImplementedError()
        case XSD.complex_content:
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()

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


def _set_attribute(element: _Element, attribute_definition: _Element) -> None:
    name = attribute_definition.get("name")
    type = attribute_definition.get("type")
    required = attribute_definition.get("use") == "required"

    if name is None:
        raise InvalidXSDError()

    do_not_create = random.random() > 0.5
    if not required and do_not_create:
        return

    if type in BuiltInType:
        element.attrib[name] = random_build_in_type(BuiltInType(type))
        return

    if type is not None:
        # lookup simple type definition
        raise NotImplementedError()

    simple_type = next(attribute_definition.iterchildren(XSD.simple_type))
    element.attrib[name] = _generate_simple_type(simple_type)


def _generate_simple_type(simple_type: _Element) -> str:
    child = next(simple_type.iterchildren())

    match child.tag:
        case XSD.list:
            raise NotImplementedError()
        case XSD.union:
            raise NotImplementedError()
        case XSD.restriction:
            return _generate_restricted(child)
        case _:
            raise InvalidXSDError()


def _generate_restricted(restriction: _Element) -> str:
    base = restriction.get("base")
    if base is None:
        raise InvalidXSDError()

    if base not in BuiltInType:
        raise NotImplementedError()

    # Assuming the enumerations are correct
    enumerations = list(restriction.iterchildren(XSD.enumeration))
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


def _generate_simple_content(simple_content: _Element) -> str:
    child = next(simple_content.iterchildren())

    match child.tag:
        case XSD.restriction:
            raise NotImplementedError()
        case XSD.extension:
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()
