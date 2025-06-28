import random

from .etree import _Element
from . import placeholder as ph, attribute, types
from .utils import XSD, InvalidXSDError
from .builtins import BuiltIn, random_built_in_type


def _find_complex_type_definition(xsd_element: _Element) -> _Element:
    complex_type = types._find_type_definition(xsd_element)
    if not isinstance(complex_type, _Element):
        raise InvalidXSDError()
    return complex_type


def _generate_complex_element(xsd_element: _Element) -> ph.Element:
    from . import element

    complex_type = _find_complex_type_definition(xsd_element)
    element_name = element._get_name_attribute(xsd_element)

    placholder = _generate_complex_type(complex_type)
    placholder.tag = element_name

    return placholder


def _generate_complex_type(xsd_complex_type: _Element) -> ph.Element:
    main_child = next(el for el in xsd_complex_type.children if el.tag != XSD.attribute)

    match main_child.tag:
        case XSD.sequence | XSD.choice | XSD.all:
            children = _recurse_indicator(main_child)
            created_element = ph.Element()
            created_element.children.extend(children)
            created_element.attrib = attribute._generate(xsd_complex_type)
        case XSD.simple_content:
            restriction_or_extension = next(main_child.children)
            created_element = ph.Element()
            created_element.text = _generate_simple_content_text(main_child)
            created_element.attrib = attribute._generate(restriction_or_extension)
        case XSD.complex_content:
            raise NotImplementedError()
        case _:
            raise InvalidXSDError()

    return created_element


def _recurse_indicator(indicator: _Element) -> list[ph.Element]:
    from . import element

    result: list[ph.Element] = []
    match indicator.tag:
        # Base conditions
        case XSD.element:
            return element._recursively_generate_element(indicator)
        case XSD.any:
            return element._generate_any_element(indicator)
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


def _generate_simple_content_text(simple_content: _Element) -> str:
    restriction_or_extension = next(simple_content.children)
    base = restriction_or_extension.get_resolved_attribute("base")

    if base not in BuiltIn:
        raise NotImplementedError()
    base = BuiltIn(base)

    match restriction_or_extension.tag:
        case XSD.restriction:
            raise NotImplementedError()
        case XSD.extension:
            return random_built_in_type(base)
        case _:
            raise InvalidXSDError()
