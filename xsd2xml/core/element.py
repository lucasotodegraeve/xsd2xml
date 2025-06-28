import random

from .utils import InvalidXSDError
from .etree import _Element

from . import types, placeholder as ph, builtins, complex_type
from .builtins import BuiltIn
from .utils import XSD


def _recursively_generate_element(xsd_element: _Element) -> list[ph.Element]:
    random_occurs = _get_random_occurs(xsd_element)
    xsd_element = _try_resolve_reference(xsd_element)
    type_definition = types._find_type_definition(xsd_element)

    if isinstance(type_definition, BuiltIn):
        generate_element_fn = _generate_built_in_element
    elif type_definition.tag == XSD.simple_type:
        raise NotImplementedError()
    elif type_definition.tag == XSD.complex_type:
        generate_element_fn = complex_type._generate_complex_element
    else:
        raise InvalidXSDError()

    return [generate_element_fn(xsd_element) for _ in range(random_occurs)]


def _get_name_attribute(element: _Element) -> str:
    name = element.get("name")
    if name is None:
        raise InvalidXSDError()
    return name


def _try_resolve_reference(element: _Element) -> _Element:
    ref = element.get("ref")
    tag = element.tag
    if ref is not None:
        referenced_element = element.root.find(f"{tag}[@name='{ref}']")
        if referenced_element is None:
            raise InvalidXSDError()
        return referenced_element

    return element


def _generate_built_in_element(xsd_element: _Element) -> ph.Element:
    name = _get_name_attribute(xsd_element)
    generated_element = ph.Element(tag=name)
    xsd_type = xsd_element.get_resolved_attribute("type")
    if xsd_type is None or xsd_type not in BuiltIn:
        raise InvalidXSDError()
    generated_element.text = builtins.random_built_in_type(BuiltIn(xsd_type))
    return generated_element


def _generate_any_element(xsd_any: _Element) -> list[ph.Element]:
    # TODO: add something with a namespace
    random_occurs = _get_random_occurs(xsd_any)
    return [ph.Element(tag=builtins.random_string()) for _ in range(random_occurs)]


def _get_random_occurs(xsd_element: _Element) -> int:
    min_occurs = xsd_element.get("minOccurs")
    min_occurs = min_occurs if min_occurs else 1

    max_occurs = xsd_element.get("maxOccurs")
    max_occurs = max_occurs if max_occurs else 1
    max_occurs = 2 if max_occurs == "unbounded" else max_occurs

    return random.randint(int(min_occurs), int(max_occurs))
