from dataclasses import dataclass, field
from enum import Enum, auto
import xml.etree.ElementTree as ET


class ElementType(Enum):
    normal = auto()
    id = auto()
    idref = auto()


@dataclass
class Element:
    tag: str | None = None
    text: str | None = None
    attrib: dict[str, str] = field(default_factory=dict)
    children: list["Element"] = field(default_factory=list)
    marker: ElementType = ElementType.normal

    def to_element(self) -> ET.Element:
        if self.tag is None:
            raise ValueError()

        element = ET.Element(self.tag, attrib=self.attrib)
        element.text = self.text
        return element

    def _recurse_to_element(self) -> ET.Element:
        children = [child._recurse_to_element() for child in self.children]
        element = self.to_element()
        element.extend(children)
        return element

    def to_tree(self) -> ET.ElementTree:
        element = self._recurse_to_element()
        return ET.ElementTree(element)
