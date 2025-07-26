from .etree import _Element
from .builtins import BuiltIn
from .utils import InvalidXSDError
from .namespaces import xsd


def _get_inlined_type_definition(xsd_element: _Element) -> _Element:
    return next(
        el for el in xsd_element.children if el in (xsd.complexType, xsd.simpleType)
    )


def find_type_defintion_by_name(
    xsd_root: _Element, type_name: str
) -> _Element | BuiltIn:
    if type_name in BuiltIn:
        return BuiltIn(type_name)

    xsd_simple_type = xsd_root.find(f"{xsd.simpleType}[@name='{type_name}']")
    if xsd_simple_type is not None:
        return xsd_simple_type

    complex_type = xsd_root.find(f"{xsd.complexType}[@name='{type_name}']")
    if complex_type is not None:
        return complex_type

    raise InvalidXSDError()


def _find_type_definition_for_element(xsd_element: _Element) -> _Element | BuiltIn:
    type_name = xsd_element.get("type")

    _is_type_definition_inlined = type_name is None
    if _is_type_definition_inlined:
        return _get_inlined_type_definition(xsd_element)

    return find_type_defintion_by_name(xsd_element.root, type_name)
