from pathlib import Path

from xmlschema import XMLSchema
import pytest
from pytest import FixtureRequest

import xsd2xml
from tests.utils import serialize_tree

PREMIS = "tests/assets/premis.xsd.xml"
premis_xsd = XMLSchema(PREMIS)


ET.register_namespace("premis", "http://www.loc.gov/premis/v3")


def is_valid(request: pytest.FixtureRequest, xsd_element_name: str, fuzzy_i: int):
    write = bool(request.config.option.write)
    tree = serialize_tree(xsd2xml.generate(PREMIS, xsd_element_name))

    output_dir = Path("output")
    if write:
        if not output_dir.exists():
            output_dir.mkdir()

        path = output_dir.joinpath(f"{xsd_element_name}_{fuzzy_i}")
        path.write_text(tree)

    return premis_xsd.is_valid(tree)


def test_agent_identifier_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "agentIdentifier", fuzzy_i)


def test_agent_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "agent", fuzzy_i)


def test_event_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "event", fuzzy_i)


def test_preservation_level_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "preservationLevel", fuzzy_i)


def test_significant_properties_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "significantProperties", fuzzy_i)


def test_object_characteristics_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "objectCharacteristics", fuzzy_i)


def test_original_name_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "originalName", fuzzy_i)


def test_storage_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "storage", fuzzy_i)


def test_signature_information_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "signatureInformation", fuzzy_i)


def test_relationship_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "relationship", fuzzy_i)


def test_linking_event_identifier_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "linkingEventIdentifier", fuzzy_i)


def test_linking_rights_statement_identifier_valid(
    request: FixtureRequest, fuzzy_i: int
):
    assert is_valid(request, "linkingRightsStatementIdentifier", fuzzy_i)


def test_object_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "object", fuzzy_i)


def test_premis_valid(request: FixtureRequest, fuzzy_i: int):
    assert is_valid(request, "premis", fuzzy_i)
