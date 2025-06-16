from xmlschema import XMLSchema
import pytest

import xsd2xml
from tests.utils import serialize_tree

MODS = "tests/assets/mods-3-7.xsd.xml"


@pytest.fixture
def mods_xsd() -> XMLSchema:
    return XMLSchema(MODS)


def test_abstract_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "abstract")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_access_condition_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "accessCondition")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_classification_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "classification")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_extension_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "extension")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_genre_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "genre")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_identifier_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "identifier")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_language_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "language")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_location_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "location")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_name_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "name")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_note_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "note")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_origin_info_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "originInfo")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_part_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "part")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_physical_description_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "physicalDescription")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_record_info_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "recordInfo")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_related_item_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "relatedItem")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_subject_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "subject")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_table_of_contents_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "tableOfContents")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_target_audience_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "targetAudience")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_title_info_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "titleInfo")
    assert mods_xsd.is_valid(serialize_tree(doc))


def test_type_of_resource_valid(mods_xsd: XMLSchema):
    doc = xsd2xml.generate(MODS, "typeOfResource")
    assert mods_xsd.is_valid(serialize_tree(doc))
