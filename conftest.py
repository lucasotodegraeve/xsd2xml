import random
import xml.etree.ElementTree as ET

import pytest

from xsd2xml.utils import ns


@pytest.fixture(autouse=True)
def set_seed():
    random.seed(1)


@pytest.fixture(autouse=True, scope="session")
def register_namespaces():
    for k, v in ns.items():
        ET.register_namespace(k, v)
