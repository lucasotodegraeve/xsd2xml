import random
from typing import Generator

from .etree import _Element
from . import placeholder as ph, attribute, types, helpers
from .utils import InvalidXSDError
from .namespaces import xsi, xsd
from .types import find_type_defintion_by_name
from .simple_type import generate_simple_type
from .builtins import BuiltIn, random_built_in_type


def _find_complex_type_definition(xsd_element: _Element) -> _Element:
    xsd_complex_type = types._find_type_definition_for_element(xsd_element)
    if (
        not isinstance(xsd_complex_type, _Element)
        or xsd_complex_type.tag != xsd.complexType
    ):
        raise InvalidXSDError()
    return xsd_complex_type


def generate_complex_element(xsd_element: _Element) -> ph.Element:
    xsd_complex_type = _find_complex_type_definition(xsd_element)
    element_name = helpers.get_element_name(xsd_element)

    placholder = _generate_complex_type_or_derivative(xsd_complex_type)
    placholder.tag = element_name

    return placholder


def _equal_complex_types(type_1: _Element, type_2: _Element) -> bool:
    t1_name = helpers._get_name_attribute(type_1)
    t2_name = helpers._get_name_attribute(type_2)
    return t1_name == t2_name


def _is_directly_derived_from(base_type: _Element, derived_type: _Element) -> bool:
    derived_main_child = next(
        filter(attribute._is_not_xsd_attribute, derived_type.children), None
    )

    if derived_main_child is None:
        return False

    content_tags = (xsd.simpleContent, xsd.complexContent)
    if derived_main_child.tag not in content_tags:
        return False

    extension_or_restriction = next(derived_main_child.children)
    base_type_name = helpers._get_name_attribute(base_type)
    return extension_or_restriction.get("base") == base_type_name


def _collect_derived_types(
    xsd_complex_type: _Element,
) -> Generator[_Element, None, None]:
    all_complex_types = xsd_complex_type.root.findall(xsd.complexType)

    for complex_type in all_complex_types:
        # A complex type is not a derivative of itself
        if _equal_complex_types(xsd_complex_type, complex_type):
            continue
        if not _is_directly_derived_from(xsd_complex_type, complex_type):
            continue

        yield complex_type

        derived_from_derived_type = _collect_derived_types(complex_type)
        for type in derived_from_derived_type:
            yield type


def _generate_complex_type_or_derivative(xsd_complex_type: _Element) -> ph.Element:
    """
    Generate a placeholder Element that has type `xsd_complex_type`
    or a complex type that extends or restricts it.
    """

    derivatives = list(_collect_derived_types(xsd_complex_type))
    is_abstract = xsd_complex_type.get("abstract", False)
    if not is_abstract:
        derivatives.append(xsd_complex_type)

    random_complex_type = random.choice(derivatives)
    created_element = _generate_complex_type(random_complex_type)

    if random_complex_type != xsd_complex_type:
        name = helpers.get_element_name(random_complex_type)
        created_element.attrib[xsi.type] = name

    return created_element


def _generate_complex_type(xsd_complex_type: _Element) -> ph.Element:
    """
    Generate a placeholder Element with a complex type.
    This function does not look for any derivatives of the given complex type.
    """
    main_child = next(
        filter(attribute._is_not_xsd_attribute, xsd_complex_type.children), None
    )

    complex_type_is_empty = main_child is None
    if complex_type_is_empty:
        return ph.Element()

    match main_child.tag:
        case xsd.sequence | xsd.choice | xsd.all:
            children = _recurse_indicator(main_child)
            created_element = ph.Element()
            created_element.children.extend(children)
            created_element.attrib = attribute._generate_attributes(xsd_complex_type)
        case xsd.simpleContent:
            created_element = _generate_simple_content(main_child)
        case xsd.complexContent:
            created_element = _generate_complex_content(main_child)
        case _:
            raise InvalidXSDError()

    return created_element


def _recurse_indicator(indicator: _Element) -> list[ph.Element]:
    from . import element

    result: list[ph.Element] = []
    match indicator.tag:
        # Base conditions
        case xsd.element:
            return element.generate_element(indicator)
        case xsd.any:
            return element._generate_any_element(indicator)
        # Recursive conditions
        case xsd.sequence:
            for child in indicator.children:
                result.extend(_recurse_indicator(child))
        case xsd.choice:
            choice = random.choice(list(indicator.children))
            result = _recurse_indicator(choice)
        case xsd.all:
            for child in indicator.children:
                result.extend(_recurse_indicator(child))
            random.shuffle(result)
        case _:
            raise NotImplementedError()

    return result


def _generate_simple_content(xsd_simple_content: _Element) -> ph.Element:
    restriction_or_extension = next(xsd_simple_content.children)

    match restriction_or_extension.tag:
        case xsd.restriction:
            raise NotImplementedError()
        case xsd.extension:
            return _generate_simple_content_extension(restriction_or_extension)

    raise InvalidXSDError()


def _generate_simple_content_extension(xsd_extension) -> ph.Element:
    base = xsd_extension.get("base")
    if base is None:
        raise InvalidXSDError()

    xsd_type = find_type_defintion_by_name(xsd_extension.root, base)

    if isinstance(xsd_type, BuiltIn):
        text = random_built_in_type(xsd_type)
        ph_element = ph.Element(text=text)
    elif xsd_type.tag == xsd.simplType:
        ph_element = generate_simple_type(xsd_type)
    elif xsd_type.tag == xsd.complexType:
        ph_element = _generate_complex_type(xsd_type)
    else:
        raise AssertionError()

    ph_element.attrib |= attribute._generate_attributes(xsd_extension)
    return ph_element


def _generate_complex_content(xsd_complex_content: _Element) -> ph.Element:
    restriction_or_extension = next(xsd_complex_content.children)

    match restriction_or_extension.tag:
        case xsd.restriction:
            raise NotImplementedError()
        case xsd.extension:
            return _generate_complex_content_extension(restriction_or_extension)

    raise InvalidXSDError()


def _generate_complex_content_extension(xsd_extension: _Element) -> ph.Element:
    base = xsd_extension.get("base")
    if base is None:
        raise InvalidXSDError()
    xsd_type = find_type_defintion_by_name(xsd_extension.root, base)

    if not (isinstance(xsd_type, _Element) and xsd_type.tag == xsd.complexType):
        raise InvalidXSDError()

    ph_element = _generate_complex_type(xsd_type)
    ph_extension_element = _generate_complex_type(xsd_extension)

    ph_element.children += ph_extension_element.children
    ph_element.attrib |= ph_extension_element.attrib

    return ph_element
