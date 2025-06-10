from enum import Enum

ns = {"xsd": "http://www.w3.org/2001/XMLSchema"}


class InvalidXSDError(Exception): ...


class XSD(str, Enum):
    element = "xsd:element"
    sequence = "xsd:sequence"
    choice = "xsd:choice"
    all = "xsd:all"
    any = "xsd:any"
    attribute = "xsd:attribute"
    any_attribute = "xsd:anyAttribute"
    complex_type = "xsd:complexType"
    simple_type = "xsd:simpleType"
    simple_content = "xsd:simpleContent"
    complex_content = "xsd:complexContent"
    attribute_group = "xsd:attributeGroup"
    group = "xsd:group"
    list = "xsd:list"
    restriction = "xsd:restriction"
    extension = "xsd:extension"
    union = "xsd:union"
    enumeration = "xsd:enumeration"
    length = "xsd:length"
    id = "xsd:ID"
    idref = "xsd:IDREF"
    idrefs = "xsd:IDREFS"
