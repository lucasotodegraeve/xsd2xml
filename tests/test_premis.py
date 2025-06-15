from xmlschema import XMLSchema
import pytest

import xsd2xml
from tests.utils import serialize_tree

PREMIS = "tests/assets/premis.xsd.xml"


@pytest.fixture
def premis_xsd() -> XMLSchema:
    return XMLSchema(PREMIS)


def test_agent_identifier_valid(premis_xsd: XMLSchema):
    doc = xsd2xml.generate(PREMIS, "agentIdentifier")
    assert premis_xsd.is_valid(serialize_tree(doc))


def test_agent(premis_xsd: XMLSchema):
    doc = xsd2xml.generate(PREMIS, "agent")
    assert premis_xsd.is_valid(serialize_tree(doc))
