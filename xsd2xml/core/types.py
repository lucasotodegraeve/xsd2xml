from xsd2xml.core.etree import _Element
from xsd2xml.core.builtins import BuiltIn
from xsd2xml.core.utils import InvalidXSDError, XSD


def _is_type_definition_inlined(xsd_element: _Element) -> bool:
    return xsd_element.get_resolved_attribute("type") is None


def _get_inlined_type_definition(xsd_element: _Element) -> _Element:
    return next(
        el for el in xsd_element.children if el in (XSD.complex_type, XSD.simple_type)
    )


def _find_type_definition(xsd_element: _Element) -> _Element | BuiltIn:
    type = xsd_element.get_resolved_attribute("type")
    if type in BuiltIn:
        return BuiltIn(type)

    if _is_type_definition_inlined(xsd_element):
        return _get_inlined_type_definition(xsd_element)

    xsd_simple_type = xsd_element.root.find(f"xsd:simpleType[@name='{type}']")
    if xsd_simple_type is not None:
        return xsd_simple_type

    complex_type = xsd_element.root.find(f"xsd:complexType[@name='{type}']")
    if complex_type is not None:
        return complex_type

    raise InvalidXSDError()
