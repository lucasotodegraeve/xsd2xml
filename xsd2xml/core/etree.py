from typing import Generator, Self, cast
import xml.etree.ElementTree as ET

from .namespaces import xsd


class _Element:
    def __init__(
        self,
        element: ET.Element,
        /,
        root: ET.Element,
    ):
        self._root = root
        self._element = element

    @property
    def attrib(self) -> dict[str, str]:
        return self._element.attrib

    @property
    def tag(self) -> str:
        return self._element.tag

    @property
    def text(self) -> str | None:
        return self._element.text

    @property
    def children(self) -> "Generator[_Element]":
        for child in self._element:
            yield _Element(child, root=self._root)

    @property
    def root(self) -> "_Element":
        return _Element(self._root, root=self._root)

    def get[_T](self, key: str, default: _T = None) -> str | _T:
        value = self._element.get(key)
        if value is None:
            return default
        return value

    # def get_resolved_attribute(self, key: str) -> str:
    #     value = self._element.get(key)
    #     if value is None:
    #         raise InvalidXSDError()
    #     return self._apply_user_namespace(value)

    def find(
        self, path: str, namespaces: dict[str, str] | None = None
    ) -> "_Element | None":
        _ = namespaces
        element = self._element.find(path)
        if element is None:
            return None
        return _Element(element, root=self._root)

    def findall(  # type: ignore[reportIncompatibleMethodOverride]
        self, path: str, namespaces: dict[str, str] | None = None
    ) -> "list[_Element]":
        _ = namespaces
        elements = self._element.findall(path)

        return [_Element(el, root=self._root) for el in elements]

    def resolve_reference(self) -> "_Element":
        ref = self.get("ref")
        if ref is not None:
            ref_element = self.root.find(f"{xsd.element}[@name='{ref}']")
            if ref_element is None:
                raise ValueError()
            return ref_element
        return self


class _ElementTree:
    def __init__(self, tree: ET.ElementTree, nsmap: dict[str, str]) -> None:
        self._tree = tree
        self._namespaces = nsmap

    @classmethod
    def parse(cls, path: str) -> Self:
        namespaces = [
            ns_tuple for _, ns_tuple in ET.iterparse(path, events=["start-ns"])
        ]
        namespaces = dict(cast(list[tuple[str, str]], namespaces))
        tree = ET.parse(path)
        _ = _expand_qname_attributes(tree.getroot(), namespaces)
        return cls(tree, namespaces)  # pyright: ignore[reportArgumentType]

    def getroot(self) -> _Element:
        xsd_root = self._tree.getroot()
        if xsd_root is None:
            raise ValueError()

        return _Element(xsd_root, root=xsd_root)


def _expand_qname_attributes(
    element: ET.Element, document_namespaces: dict[str, str]
) -> ET.Element:
    """
    Certain attributes may have a prefixed value e.g. xsi:type="schema:Episode".
    Expand the prefixed attribute value to its full qualified name e.g. "{https://schema.org/}Episode"
    """

    for k, v in element.attrib.items():
        if k == "base" or k == "type":
            element.attrib[k] = _expand_qname(v, document_namespaces)

    for child in element:
        _ = _expand_qname_attributes(child, document_namespaces)

    return element


def _expand_qname(name: str, document_namespaces: dict[str, str]) -> str:
    """
    Expand a prefixed qualified name to its fully qualified name.
    E.g. "schema:Episode" is expanded to "{https://schema.org/}Episode"
    """

    if ":" not in name:
        return name

    splitted_qname = name.split(":", 1)
    prefix = splitted_qname[0]
    local = splitted_qname[1]
    prefix_iri = document_namespaces[prefix]

    return "{" + prefix_iri + "}" + local
