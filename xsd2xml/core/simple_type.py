import random

from .utils import InvalidXSDError, XSD
from .etree import _Element

from .builtins import BuiltIn


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

    is_type_user_defined = base not in BuiltIn
    if is_type_user_defined:
        raise NotImplementedError()

    # Assuming the enumerations are correct
    enumerations = restriction.findall(XSD.enumeration)
    has_enumerations = len(enumerations) != 0
    if has_enumerations:
        return _choose_restriction_enumeration(enumerations)

    base = BuiltIn(base)
    match base:
        case BuiltIn.string:
            raise NotImplementedError()
        case _:
            raise NotImplementedError()


def _choose_restriction_enumeration(enumerations: list[_Element]) -> str:
    enum_choice = random.choice(enumerations)
    enum_value = enum_choice.get("value")
    if enum_value is None:
        raise InvalidXSDError()
    return enum_value
