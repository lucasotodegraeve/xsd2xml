import random
from typing import Iterable, cast
import xml.etree.ElementTree as ET

from .element_wrapper import _Element

from xsd2xml.types import (
    BuiltInType,
    random_built_in_type,
    random_string,
)
from xsd2xml.utils import ns, InvalidXSDError


def generate(xsd_path: str, element_name: str) -> ET.ElementTree:
    xsd_tree = ET.parse(xsd_path)
    xsd_root = xsd_tree.getroot()

    namespaces = [
        ns_tuple for _, ns_tuple in ET.iterparse(xsd_path, events=["start-ns"])
    ]
    namespaces = dict(cast(list[tuple[str, str]], namespaces))
    xsd_root = _Element(
        xsd_root,
        doc_ns=namespaces,
        user_ns=ns,
        root=xsd_root,
    )

    xsd_element = xsd_root.find(f"xsd:element[@name='{element_name}']")
    if xsd_element is None:
        raise ValueError()

    created_element = _recursively_generate_element(xsd_element)
    created_element = next(iter(created_element))

    target_namespace = xsd_root.get("targetNamespace")
    if target_namespace is not None:
        created_element.attrib["xmlns"] = target_namespace

    return ET.ElementTree(created_element)


def _try_resolve_reference(element: _Element) -> _Element:
    ref = element.get("ref")
    tag = element.tag
    if ref is not None:
        referenced_element = element.root.find(f"{tag}[@name='{ref}']")
        if referenced_element is None:
            raise InvalidXSDError()
        return referenced_element

    return element


def _get_random_occurs(xsd_element: _Element) -> int:
    min_occurs = xsd_element.get("minOccurs")
    min_occurs = min_occurs if min_occurs else 1

    max_occurs = xsd_element.get("maxOccurs")
    max_occurs = max_occurs if max_occurs else 1
    max_occurs = 5 if max_occurs == "unbounded" else max_occurs

    return random.randint(int(min_occurs), int(max_occurs))


def _is_type_definition_inlined(xsd_element: _Element) -> bool:
    return xsd_element.get_resolved_attribute("type") is None


def _find_type_definition(xsd_element: _Element) -> _Element | BuiltInType:
    type = xsd_element.get_resolved_attribute("type")
    if type in BuiltInType:
        return BuiltInType(type)

    if _is_type_definition_inlined(xsd_element):
        return next(
            el
            for el in xsd_element.children
            if el in ("xsd:complexType", "xsd:simpleType")
        )

    simple_type = xsd_element.root.find(f"xsd:simpleType[@name='{type}']")
    if simple_type is not None:
        return simple_type

    complex_type = xsd_element.root.find(f"xsd:complexType[@name='{type}']")
    if complex_type is not None:
        return complex_type

    raise InvalidXSDError()


def _recursively_generate_element(xsd_element: _Element) -> list[ET.Element]:
    xsd_element = _try_resolve_reference(xsd_element)
    random_occurs = _get_random_occurs(xsd_element)
    type_definition = _find_type_definition(xsd_element)

    if isinstance(type_definition, BuiltInType):
        return [_create_built_in_element(xsd_element) for _ in range(random_occurs)]
    elif type_definition.tag == "xsd:simpleType":
        raise NotImplementedError()
    elif type_definition.tag == "xsd:complexType":
        return [
            _create_complex_element(xsd_element, type_definition)
            for _ in range(random_occurs)
        ]

    raise InvalidXSDError()


def _create_built_in_element(xsd_element: _Element) -> ET.Element:
    name = xsd_element.get("name")
    if name is None:
        raise InvalidXSDError()
    generated_element = ET.Element(name)
    xsd_type = xsd_element.get_resolved_attribute("type")
    if xsd_type is None or xsd_type not in BuiltInType:
        raise InvalidXSDError()
    generated_element.text = random_built_in_type(BuiltInType(xsd_type))
    return generated_element


def _create_complex_element(
    xsd_element: _Element, complex_type: _Element
) -> ET.Element:
    element_name = xsd_element.get("name")
    if element_name is None:
        raise InvalidXSDError()

    main_child = next(el for el in complex_type.children if el.tag != "xsd:attribute")

    match main_child.tag:
        case "xsd:sequence" | "xsd:choice" | "xsd:all":
            created_element = ET.Element(element_name)
            _set_attributes(
                created_element,
                (el for el in complex_type.children if el.tag == "xsd:attribute"),
            )

            children = _recurse_indicator(main_child)
            created_element.extend(children)
        case "xsd:simpleContent":
            created_element = ET.Element(element_name)
            return _generate_simple_content(created_element, main_child)
        case "xsd:complexContent":
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()

    return created_element


def _recurse_indicator(indicator: _Element) -> list[ET.Element]:
    result: list[ET.Element] = []
    match indicator.tag:
        case "xsd:element":
            # Base condition
            return _recursively_generate_element(indicator)
        case "xsd:any":
            return _create_any_element(indicator)
        case "xsd:sequence":
            for child in indicator.children:
                result.extend(_recurse_indicator(child))
        case "xsd:choice":
            choice = random.choice(list(indicator.children))
            result = _recurse_indicator(choice)
        case "xsd:all":
            for child in indicator.children:
                result.extend(_recurse_indicator(child))
            random.shuffle(result)
        case _:
            raise NotImplementedError()

    return result


def _set_attributes(
    created_element: ET.Element,
    xsd_attribute_list: Iterable[_Element],
) -> None:
    for xsd_attribute in xsd_attribute_list:
        xsd_attribute = _try_resolve_reference(xsd_attribute)

        if xsd_attribute.tag == "xsd:attributeGroup":
            xsd_attribute_group = _try_resolve_reference(xsd_attribute)
            _set_attributes(
                created_element, (el for el in xsd_attribute_group.children)
            )

        if xsd_attribute.tag == "xsd:anyAttribute":
            raise NotImplementedError()

        name = xsd_attribute.get("name")
        type = xsd_attribute.get_resolved_attribute("type")

        required = xsd_attribute.get("use") == "required"

        if name is None:
            raise InvalidXSDError()

        do_not_create = random.random() > 0.5
        if not required and do_not_create:
            continue

        if type == "xsd:IDREF":
            # Not supported currently
            continue

        if type in BuiltInType:
            created_element.attrib[name] = random_built_in_type(BuiltInType(type))
            continue

        is_type_user_defined = type is not None and type not in BuiltInType
        if is_type_user_defined:
            raise NotImplementedError()

        is_type_anonymous = type is None
        if is_type_anonymous:
            simple_type = next(
                el for el in xsd_attribute.children if el.tag == "xsd:simpleType"
            )
            created_element.attrib[name] = _generate_simple_type(simple_type)
            continue


def _generate_simple_type(simple_type: _Element) -> str:
    child = next(simple_type.children)

    match child.tag:
        case "xsd:list":
            raise NotImplementedError()
        case "xsd:union":
            raise NotImplementedError()
        case "xsd:restriction":
            return _generate_restricted(child)
        case _:
            raise InvalidXSDError()


def _generate_restricted(restriction: _Element) -> str:
    base = restriction.get_resolved_attribute("base")
    if base is None:
        raise InvalidXSDError()

    if base not in BuiltInType:
        raise NotImplementedError()

    # Assuming the enumerations are correct
    enumerations = [el for el in restriction.children if el.tag == "xsd:enumeration"]

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
    created_element: ET.Element, simple_content: _Element
) -> ET.Element:
    restriction_or_extension = next(simple_content.children)
    base = restriction_or_extension.get_resolved_attribute("base")
    if base is None:
        raise InvalidXSDError()

    if base not in BuiltInType:
        raise NotImplementedError()
    base = BuiltInType(base)

    match restriction_or_extension.tag:
        case "xsd:restriction":
            raise NotImplementedError()
        case "xsd:extension":
            created_element.text = random_built_in_type(base)
            _set_attributes(
                created_element,
                (
                    el
                    for el in restriction_or_extension.children
                    if el == "xsd:attribute"
                ),
            )
            return created_element
        case _:
            raise InvalidXSDError()


def _create_any_element(xsd_any: _Element) -> list[ET.Element]:
    # TODO: add something with a namespace
    random_occurs = _get_random_occurs(xsd_any)
    return [ET.Element(random_string()) for _ in range(random_occurs)]
