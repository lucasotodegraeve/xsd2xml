import random

from . import simple_type, helpers

from .etree import _Element
from .utils import InvalidXSDError
from .namespaces import xsd

from xsd2xml.core.builtins import BuiltIn, random_built_in_type


def _recursively_collect_attributes(
    element_with_xsd_attributes: _Element,
) -> list[_Element]:
    attributes = element_with_xsd_attributes.findall(xsd.attribute)
    attributes += element_with_xsd_attributes.findall(xsd.anyAttribute)
    attribute_groups = element_with_xsd_attributes.findall(xsd.attributeGroup)

    for group_or_reference in attribute_groups:
        xsd_attribute_group = helpers._try_resolve_reference(group_or_reference)
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

        if xsd_attribute.tag == xsd.attribute:
            attribute_name = helpers._get_name_attribute(xsd_attribute)
            attrib[attribute_name] = _generate_attribute_value(xsd_attribute)
        elif xsd_attribute.tag == xsd.anyAttribute:
            attrib |= _generate_any_attribute()
        else:
            raise InvalidXSDError()

    return attrib


def _generate_any_attribute() -> dict[str, str]:
    raise NotImplementedError()


def _generate_attribute_value(xsd_attribute: _Element) -> str:
    type = xsd_attribute.get("type")
    if type in BuiltIn:
        return random_built_in_type(BuiltIn(type))

    is_type_user_defined = type is not None and type not in BuiltIn
    if is_type_user_defined:
        xsd_simple_type = xsd_attribute.root.find(f"{xsd.simpleType}[@name='{type}']")
        if xsd_simple_type is None:
            raise InvalidXSDError()
        ph_element = simple_type.generate_simple_type(xsd_simple_type)
        if ph_element.text is None:
            raise AssertionError()
        return ph_element.text

    is_type_anonymous = type is None
    if is_type_anonymous:
        xsd_simple_type = xsd_attribute.find(xsd.simpleType)
        if xsd_simple_type is None:
            raise InvalidXSDError()
        ph_element = simple_type.generate_simple_type(xsd_simple_type)
        if ph_element.text is None:
            raise AssertionError()
        return ph_element.text

    raise InvalidXSDError()


def _is_xsd_attribute(element: _Element) -> bool:
    return element.tag in (xsd.attribute, xsd.attributeGroup, xsd.anyAttribute)


def _is_not_xsd_attribute(element: _Element) -> bool:
    return not _is_xsd_attribute(element)
