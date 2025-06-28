from xmlschema import XMLSchema
import pytest

import xsd2xml
from tests.utils import serialize_tree, set_seed

PREMIS = "tests/assets/premis.xsd.xml"


@pytest.fixture
def premis_xsd() -> XMLSchema:
    return XMLSchema(PREMIS)


@pytest.mark.parametrize("i", range(10))
def test_agent_identifier_valid(premis_xsd: XMLSchema, i: int):
    set_seed(i)
    tree = xsd2xml.generate(PREMIS, "agentIdentifier")
    assert premis_xsd.is_valid(serialize_tree(tree))


@pytest.mark.parametrize("i", range(10))
def test_agent(premis_xsd: XMLSchema, i: int):
    set_seed(i)
    tree = xsd2xml.generate(PREMIS, "agent")
    assert premis_xsd.is_valid(serialize_tree(tree))


@pytest.mark.parametrize("i", range(10))
def test_event(premis_xsd: XMLSchema, i: int):
    set_seed(i)
    tree = xsd2xml.generate(PREMIS, "event")
    assert premis_xsd.is_valid(serialize_tree(tree))
