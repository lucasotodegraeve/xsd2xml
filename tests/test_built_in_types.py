import random
from typing import Any

import pytest
import xmlschema
from lxml import etree

import xsd2xml.types as types
from xsd2xml.utils import ns


@pytest.fixture(autouse=True)
def set_seed():
    random.seed(1)


def _test_type(type_name: str, value: Any):
    xsd_schema = etree.Element("{http://www.w3.org/2001/XMLSchema}schema", nsmap=ns)
    xsd_element = etree.Element(
        "{http://www.w3.org/2001/XMLSchema}element",
        attrib={"name": "test", "type": type_name},
    )
    xsd_schema.append(xsd_element)

    xml_element = etree.Element("test")
    xml_element.text = value

    schema = xmlschema.XMLSchema(source=xsd_schema)  # type: ignore
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
