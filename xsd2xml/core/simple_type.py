import random
from typing import Generator

from .utils import InvalidXSDError
from .etree import _Element
from .namespaces import xsd, xsi
from . import placeholder as ph, types, helpers

from .builtins import BuiltIn
from xsd2xml.core import builtins


def _find_simple_type_definition(xsd_element: _Element) -> _Element:
    xsd_simple_type = types._find_type_definition_for_element(xsd_element)
    if (
        not isinstance(xsd_simple_type, _Element)
        or xsd_simple_type.tag != xsd.simpleType
    ):
        raise InvalidXSDError()
    return xsd_simple_type


def generate_simple_element(xsd_element: _Element) -> ph.Element:
    complex_type = _find_simple_type_definition(xsd_element)
    element_name = helpers.get_element_name(xsd_element)

    placholder = _generate_simple_type_or_derivative(complex_type)
    placholder.tag = element_name

    return placholder


def generate_simple_type(xsd_simple_type: _Element) -> ph.Element:
    child = next(xsd_simple_type.children)

    match child.tag:
        case xsd.list:
            raise NotImplementedError()
        case xsd.union:
            raise NotImplementedError()
        case xsd.restriction:
            return _generate_restricted_simple_type(child)
        case _:
            raise InvalidXSDError()


def _is_directly_derived_from(base_type: _Element, derived_type: _Element) -> bool:
    derived_main_child = next(derived_type.children, None)

    if derived_main_child is None:
        return False

    if derived_main_child.tag != xsd.restriction:
        return False

    xsd_restriction = derived_main_child
    base_type_name = helpers._get_name_attribute(base_type)
    return xsd_restriction.get("base") == base_type_name


def equal_names(type_1: _Element, type_2: _Element) -> bool:
    t1_name = helpers._get_name_attribute(type_1)
    t2_name = helpers._get_name_attribute(type_2)
    return t1_name == t2_name


def _collect_derived_types(
    xsd_simple_type: _Element,
) -> Generator[_Element, None, None]:
    all_simple_types = xsd_simple_type.root.findall(xsd.simpleType)

    for simple_type in all_simple_types:
        # A simple type is not a derivative of itself
        if equal_names(xsd_simple_type, simple_type):
            continue
        if not _is_directly_derived_from(xsd_simple_type, simple_type):
            continue

        yield simple_type

        derived_from_derived_type = _collect_derived_types(simple_type)
        for type in derived_from_derived_type:
            yield type


def _generate_simple_type_or_derivative(xsd_simple_type: _Element) -> ph.Element:
    derivatives = list(_collect_derived_types(xsd_simple_type))
    is_abstract = xsd_simple_type.get("abstract", False)
    if not is_abstract:
        derivatives.append(xsd_simple_type)

    random_simple_type = random.choice(derivatives)
    created_element = generate_simple_type(random_simple_type)

    if random_simple_type != xsd_simple_type:
        name = helpers.get_element_name(random_simple_type)
        created_element.attrib[xsi.type] = name

    return created_element


def _generate_restricted_simple_type(xsd_restriction: _Element) -> ph.Element:
    base = xsd_restriction.get("base")
    if base is None:
        raise InvalidXSDError()

    is_type_user_defined = base not in BuiltIn
    if is_type_user_defined:
        raise NotImplementedError()

    # Assuming the enumerations are correct
    enumerations = xsd_restriction.findall(xsd.enumeration)
    has_enumerations = len(enumerations) != 0
    if has_enumerations:
        enumeration = _choose_restriction_enumeration(enumerations)
        return ph.Element(text=enumeration)

    if len(list(xsd_restriction.children)) != 0:
        # TODO: build up temporary restricted type
        raise NotImplementedError()

    text = builtins.random_built_in_type(BuiltIn(base))
    return ph.Element(text=text)


def _choose_restriction_enumeration(enumerations: list[_Element]) -> str:
    enum_choice = random.choice(enumerations)
    enum_value = enum_choice.get("value")
    if enum_value is None:
        raise InvalidXSDError()
    return enum_value
