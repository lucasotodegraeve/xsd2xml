import random


from . import simple_type
from . import element

from .etree import _Element
from .utils import InvalidXSDError, XSD

from xsd2xml.core.builtins import BuiltIn, random_built_in_type


def _recursively_collect_attributes(
    element_with_xsd_attributes: _Element,
) -> list[_Element]:
    attributes = element_with_xsd_attributes.findall(XSD.attribute)
    attributes += element_with_xsd_attributes.findall(XSD.any_attribute)
    attribute_groups = element_with_xsd_attributes.findall(XSD.attribute_group)

    for group_or_reference in attribute_groups:
        xsd_attribute_group = element._try_resolve_reference(group_or_reference)
        attributes += _recursively_collect_attributes(xsd_attribute_group)

    return attributes


def _should_skip_attribute(xsd_attribute: _Element) -> bool:
    is_attribute_required = xsd_attribute.get("use") == "required"
    do_not_create = random.random() > 0.5
    return not is_attribute_required and do_not_create


def _generate(element_with_xsd_attributes: _Element) -> dict[str, str]:
    attrib = {}
    xsd_attributes = _recursively_collect_attributes(element_with_xsd_attributes)
    for xsd_attribute in xsd_attributes:
        if _should_skip_attribute(xsd_attribute):
            continue

        if xsd_attribute.tag == XSD.attribute:
            attribute_name = element._get_name_attribute(xsd_attribute)
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
    if type in BuiltIn:
        return random_built_in_type(BuiltIn(type))

    is_type_user_defined = type is not None and type not in BuiltIn
    if is_type_user_defined:
        xsd_simple_type = xsd_attribute.root.find(f"xsd:simpleType[@name='{type}']")
        if xsd_simple_type is None:
            raise InvalidXSDError()
        return simple_type._generate_simple_type(xsd_simple_type)

    is_type_anonymous = type is None
    if is_type_anonymous:
        xsd_simple_type = xsd_attribute.find(XSD.simple_type)
        if xsd_simple_type is None:
            raise InvalidXSDError()
        return simple_type._generate_simple_type(xsd_simple_type)

    raise InvalidXSDError()
