from dataclasses import dataclass, field
from enum import Enum, auto
import xml.etree.ElementTree as ET

from xsd2xml.core.namespaces import xsi


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

    def manifest(self) -> ET.Element:
        if self.tag is None:
            raise ValueError()

        element = ET.Element(self.tag, attrib=self.attrib)
        element.text = self.text
        return element

    def manifest_placeholders(self) -> ET.Element:
        children = [child.manifest_placeholders() for child in self.children]
        element = self.manifest()
        element.extend(children)
        return element

    def to_tree(self) -> ET.ElementTree:
        element = self.manifest_placeholders()
        return ET.ElementTree(element)
