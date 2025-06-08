from typing import Any
import xml.etree.ElementTree as ET
import io

import xmlschema

import xsd2xml.types as types


def _test_type(xsd_type_name: str, value: Any):
    xsd_schema = ET.Element(
        "{http://www.w3.org/2001/XMLSchema}schema",
    )
    xsd_element = ET.Element(
        "{http://www.w3.org/2001/XMLSchema}element",
        attrib={"name": "test", "type": xsd_type_name},
    )
    xsd_schema.append(xsd_element)
    xsd_tree = ET.ElementTree(xsd_schema)

    data = io.StringIO()
    xsd_tree.write(data, encoding="unicode")
    serialized = data.getvalue()

    xml_element = ET.Element("test")
    xml_element.text = value

    schema = xmlschema.XMLSchema(source=serialized)
    assert schema.is_valid(xml_element)


def test_string():
    for _ in range(100):
        _test_type("xsd:string", types.random_string())


def test_boolean():
    for _ in range(100):
        _test_type("xsd:boolean", types.random_boolean())


def test_decimal():
    for _ in range(100):
        _test_type("xsd:decimal", types.random_decimal())


def test_float():
    for _ in range(100):
        _test_type("xsd:float", types.random_float())


def test_double():
    for _ in range(100):
        _test_type("xsd:double", types.random_double())


def test_duration():
    for _ in range(100):
        _test_type("xsd:duration", types.random_duration())


def test_integer():
    for _ in range(100):
        _test_type("xsd:integer", types.random_integer())
