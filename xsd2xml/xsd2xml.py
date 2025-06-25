import random
import xml.etree.ElementTree as ET

from .element_wrapper import _Element, _ElementTree, Placeholder

from xsd2xml.types import (
    BuiltInType,
    IDMarker,
    IDREFMarker,
    random_built_in_type,
    random_string,
)
from xsd2xml.utils import InvalidXSDError, XSD


def generate(xsd_path: str, element_name: str) -> ET.ElementTree:
    xsd_tree = _ElementTree.parse(xsd_path)
    xsd_root = xsd_tree.getroot()

    xsd_element = xsd_root.find(f"xsd:element[@name='{element_name}']")
    if xsd_element is None:
        raise ValueError()

    created_element = _recursively_generate_element(xsd_element)
    created_element = next(iter(created_element))._to_tree()

    _recurse_markers(created_element)

    target_namespace = xsd_root.get("targetNamespace")
    if target_namespace is not None:
        created_element.attrib["xmlns"] = target_namespace

    return ET.ElementTree(created_element)


def _recurse_markers(element: ET.Element) -> None:
    ids = _recurse_find_ids(element)
    _recurse_populate_idrefs(element, ids)


def _recurse_find_ids(element: ET.Element) -> list[str]:
    ids = []
    for child in element:
        ids += _recurse_find_ids(child)

    if isinstance(element.text, IDMarker):
        ids.append(element.text)

    for v in element.attrib.values():
        if isinstance(v, IDMarker):
            ids.append(v)

    return ids


def _recurse_populate_idrefs(element: ET.Element, ids: list[str]) -> None:
    if isinstance(element.text, IDREFMarker):
        element.text = random.choice(ids)

    for k, v in element.attrib.items():
        if isinstance(v, IDREFMarker):
            element.attrib[k] = random.choice(ids)

    for child in element:
        _recurse_populate_idrefs(child, ids)


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


def _get_inlined_type_definition(xsd_element: _Element) -> _Element:
    return next(
        el for el in xsd_element.children if el in (XSD.complex_type, XSD.simple_type)
    )


def _find_type_definition(xsd_element: _Element) -> _Element | BuiltInType:
    type = xsd_element.get_resolved_attribute("type")
    if type in BuiltInType:
        return BuiltInType(type)

    if _is_type_definition_inlined(xsd_element):
        return _get_inlined_type_definition(xsd_element)

    simple_type = xsd_element.root.find(f"xsd:simpleType[@name='{type}']")
    if simple_type is not None:
        return simple_type

    complex_type = xsd_element.root.find(f"xsd:complexType[@name='{type}']")
    if complex_type is not None:
        return complex_type

    raise InvalidXSDError()


def _find_complex_type_definition(xsd_element: _Element) -> _Element:
    complex_type = _find_type_definition(xsd_element)
    if not isinstance(complex_type, _Element):
        raise InvalidXSDError()
    return complex_type


def _recursively_generate_element(xsd_element: _Element) -> list[Placeholder]:
    random_occurs = _get_random_occurs(xsd_element)
    xsd_element = _try_resolve_reference(xsd_element)
    type_definition = _find_type_definition(xsd_element)

    if isinstance(type_definition, BuiltInType):
        generate_element_fn = _generate_built_in_element
    elif type_definition.tag == XSD.simple_type:
        raise NotImplementedError()
    elif type_definition.tag == XSD.complex_type:
        generate_element_fn = _generate_complex_element
    else:
        raise InvalidXSDError()

    return [generate_element_fn(xsd_element) for _ in range(random_occurs)]


def _generate_built_in_element(xsd_element: _Element) -> Placeholder:
    name = _get_name_attribute(xsd_element)
    generated_element = Placeholder(tag=name)
    xsd_type = xsd_element.get_resolved_attribute("type")
    if xsd_type is None or xsd_type not in BuiltInType:
        raise InvalidXSDError()
    generated_element.text = random_built_in_type(BuiltInType(xsd_type))
    return generated_element


def _generate_complex_element(xsd_element: _Element) -> Placeholder:
    complex_type = _find_complex_type_definition(xsd_element)
    element_name = _get_name_attribute(xsd_element)

    main_child = next(el for el in complex_type.children if el.tag != XSD.attribute)

    match main_child.tag:
        case XSD.sequence | XSD.choice | XSD.all:
            children = _recurse_indicator(main_child)
            created_element = Placeholder(tag=element_name)
            created_element.children.extend(children)
            created_element.attrib = _generate_attributes(complex_type)
        case XSD.simple_content:
            restriction_or_extension = next(main_child.children)
            created_element = Placeholder(tag=element_name)
            created_element.text = _generate_simple_content_text(main_child)
            created_element.attrib = _generate_attributes(restriction_or_extension)
        case XSD.complex_content:
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()

    return created_element


def _recursively_collect_attributes(
    element_with_xsd_attributes: _Element,
) -> list[_Element]:
    attributes = element_with_xsd_attributes.findall(XSD.attribute)
    attributes += element_with_xsd_attributes.findall(XSD.any_attribute)
    attribute_groups = element_with_xsd_attributes.findall(XSD.attribute_group)

    for group_or_reference in attribute_groups:
        xsd_attribute_group = _try_resolve_reference(group_or_reference)
        attributes += _recursively_collect_attributes(xsd_attribute_group)

    return attributes


def _should_skip_attribute(xsd_attribute: _Element) -> bool:
    is_attribute_required = xsd_attribute.get("use") == "required"
    do_not_create = random.random() > 0.5
    return not is_attribute_required and do_not_create


def _generate_attributes(element_with_xsd_attributes: _Element) -> dict[str, str]:
    attrib = {}
    xsd_attributes = _recursively_collect_attributes(element_with_xsd_attributes)
    for xsd_attribute in xsd_attributes:
        if _should_skip_attribute(xsd_attribute):
            continue

        if xsd_attribute.tag == XSD.attribute:
            attribute_name = _get_name_attribute(xsd_attribute)
            attrib[attribute_name] = _generate_attribute_value(xsd_attribute)
        elif xsd_attribute.tag == XSD.any_attribute:
            attrib |= _generate_any_attribute()
        else:
            raise InvalidXSDError()

    return attrib


def _generate_any_attribute() -> dict[str, str]:
    raise NotImplementedError()


def _generate_attribute_value(xsd_attribute: _Element) -> str:
    type = xsd_attribute.get_resolved_attribute("type")
    if type in BuiltInType:
        return random_built_in_type(BuiltInType(type))

    is_type_user_defined = type is not None and type not in BuiltInType
    if is_type_user_defined:
        simple_type = xsd_attribute.root.find(f"xsd:simpleType[@name='{type}']")
        if simple_type is None:
            raise InvalidXSDError()
        return _generate_simple_type(simple_type)

    is_type_anonymous = type is None
    if is_type_anonymous:
        simple_type = xsd_attribute.find(XSD.simple_type)
        if simple_type is None:
            raise InvalidXSDError()
        return _generate_simple_type(simple_type)

    raise InvalidXSDError()


def _recurse_indicator(indicator: _Element) -> list[Placeholder]:
    result: list[Placeholder] = []
    match indicator.tag:
        # Base conditions
        case XSD.element:
            return _recursively_generate_element(indicator)
        case XSD.any:
            return _generate_any_element(indicator)
        # Recursive conditions
        case XSD.sequence:
            for child in indicator.children:
                result.extend(_recurse_indicator(child))
        case XSD.choice:
            choice = random.choice(list(indicator.children))
            result = _recurse_indicator(choice)
        case XSD.all:
            for child in indicator.children:
                result.extend(_recurse_indicator(child))
            random.shuffle(result)
        case _:
            raise NotImplementedError()

    return result


def _generate_simple_type(simple_type: _Element) -> str:
    child = next(simple_type.children)

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
    base = restriction.get_resolved_attribute("base")
    if base is None:
        raise InvalidXSDError()

    is_type_user_defined = base not in BuiltInType
    if is_type_user_defined:
        raise NotImplementedError()

    # Assuming the enumerations are correct
    enumerations = restriction.findall(XSD.enumeration)
    has_enumerations = len(enumerations) != 0
    if has_enumerations:
        return _choose_restriction_enumeration(enumerations)

    base = BuiltInType(base)
    match base:
        case BuiltInType.string:
            raise NotImplementedError()
        case _:
            raise NotImplementedError()


def _choose_restriction_enumeration(enumerations: list[_Element]) -> str:
    enum_choice = random.choice(enumerations)
    enum_value = enum_choice.get("value")
    if enum_value is None:
        raise InvalidXSDError()
    return enum_value


def _generate_simple_content_text(simple_content: _Element) -> str:
    restriction_or_extension = next(simple_content.children)
    base = restriction_or_extension.get_resolved_attribute("base")

    if base not in BuiltInType:
        raise NotImplementedError()
    base = BuiltInType(base)

    match restriction_or_extension.tag:
        case XSD.restriction:
            raise NotImplementedError()
        case XSD.extension:
            return random_built_in_type(base)
        case _:
            raise InvalidXSDError()


def _generate_any_element(xsd_any: _Element) -> list[Placeholder]:
    # TODO: add something with a namespace
    random_occurs = _get_random_occurs(xsd_any)
    return [Placeholder(tag=random_string()) for _ in range(random_occurs)]


def _get_name_attribute(element: _Element) -> str:
    name = element.get("name")
    if name is None:
        raise InvalidXSDError()
    return name
