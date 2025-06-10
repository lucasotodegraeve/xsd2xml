from typing import Generator, Self, cast
import xml.etree.ElementTree as ET

from xsd2xml.utils import InvalidXSDError, ns


class _Element:
    def __init__(
        self,
        element: ET.Element,
        /,
        doc_ns: dict[str, str],
        user_ns: dict[str, str],
        root: ET.Element,
    ):
        self.document_namespaces = doc_ns
        self.user_namespaces = user_ns
        self._root = root

        self._element = element

    @property
    def attrib(self) -> dict[str, str]:
        return self._element.attrib

    @property
    def tag(self) -> str:
        tag = self._element.tag
        if not _is_tag_namespaced(tag):
            return tag

        idx = tag.find("}")
        prefix_uri = tag[1:idx]
        user_prefix = next(
            k for k, v in self.user_namespaces.items() if v == prefix_uri
        )
        return user_prefix + ":" + tag[idx + 1 :]

    @property
    def text(self) -> str | None:
        return self._element.text

    @property
    def children(self) -> "Generator[_Element]":
        for child in self._element:
            yield _Element(
                child,
                doc_ns=self.document_namespaces,
                user_ns=self.user_namespaces,
                root=self._root,
            )

    @property
    def root(self) -> "_Element":
        return _Element(
            self._root,
            doc_ns=self.document_namespaces,
            user_ns=self.user_namespaces,
            root=self._root,
        )

    def get[_T](self, key: str, default: _T = None) -> str | _T:
        value = self._element.get(key)
        if value is None:
            return default
        return value

    def get_resolved_attribute(self, key: str) -> str:
        value = self._element.get(key)
        if value is None:
            raise InvalidXSDError()
        return self._apply_user_namespace(value)

    def _apply_user_namespace(self, value: str) -> str:
        if not _is_tag_namespaced(value):
            return value

        idx = value.find(":")
        prefix = value[:idx]
        if prefix not in self.document_namespaces.keys():
            raise ValueError()

        local = value[idx + 1 :]
        prefix_uri = self.document_namespaces[prefix]
        user_prefix = next(
            k for k, v in self.user_namespaces.items() if v == prefix_uri
        )
        return user_prefix + ":" + local

    def find(
        self, path: str, namespaces: dict[str, str] | None = None
    ) -> "_Element | None":
        _ = namespaces
        element = self._element.find(path, namespaces=self.user_namespaces)
        if element is None:
            return None
        return _Element(
            element,
            doc_ns=self.document_namespaces,
            user_ns=self.user_namespaces,
            root=self._root,
        )

    def findall(  # type: ignore[reportIncompatibleMethodOverride]
        self, path: str, namespaces: dict[str, str] | None = None
    ) -> "list[_Element]":
        _ = namespaces
        elements = self._element.findall(path, namespaces=self.user_namespaces)

        return [
            _Element(
                el,
                doc_ns=self.document_namespaces,
                user_ns=self.user_namespaces,
                root=self._root,
            )
            for el in elements
        ]

    def resolve_reference(self) -> "_Element":
        ref = self.get("ref")
        if ref is not None:
            ref_element = self.root.find(f"xsd:element[@name='{ref}']")
            if ref_element is None:
                raise ValueError()
            return ref_element
        return self


def _is_tag_namespaced(tag: str) -> bool:
    return ":" in tag or "{" in tag


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
        return cls(ET.parse(path), namespaces)  # pyright: ignore[reportArgumentType]

    def getroot(self) -> _Element:
        xsd_root = self._tree.getroot()
        if xsd_root is None:
            raise ValueError()

        return _Element(
            xsd_root,
            doc_ns=self._namespaces,
            user_ns=ns,
            root=xsd_root,
        )
