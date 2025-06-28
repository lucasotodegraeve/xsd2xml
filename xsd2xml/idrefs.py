import random
import xml.etree.ElementTree as ET
from xsd2xml.builtins import IDMarker, IDREFMarker


def _recurse_markers(element: ET.Element) -> None:
    ids = _recurse_find_ids(element)
    if len(ids) == 0:
        _recurse_remove_idrefs(element)
    _recurse_populate_idrefs(element, ids)


def _recurse_find_ids(element: ET.Element) -> list[str]:
    ids = []
    for child in element:
        ids += _recurse_find_ids(child)

    if isinstance(element.text, IDMarker):
        ids.append(element.text)

    for v in element.attrib.values():
        if isinstance(v, IDMarker):
            ids.append(v)

    return ids


def _recurse_populate_idrefs(element: ET.Element, ids: list[str]) -> None:
    if isinstance(element.text, IDREFMarker):
        element.text = random.choice(ids)

    for k, v in element.attrib.items():
        if isinstance(v, IDREFMarker):
            element.attrib[k] = random.choice(ids)

    for child in element:
        _recurse_populate_idrefs(child, ids)


def _recurse_remove_idrefs(element: ET.Element) -> None:
    children = [el for el in element]
    for child in children:
        if isinstance(child.text, IDREFMarker):
            element.remove(child)

        for k, v in child.attrib.copy().items():
            if isinstance(v, IDREFMarker):
                child.attrib.pop(k)
