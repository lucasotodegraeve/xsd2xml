from .etree import _Element
from .utils import InvalidXSDError


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
