import random
import xml.etree.ElementTree as ET

import pytest

from xsd2xml.utils import ns


@pytest.fixture(autouse=True)
def _set_seed():
    random.seed(1)


@pytest.fixture(autouse=True, scope="session")
def register_namespaces():
    """
    The namespaces are registered here so that they are used as `xmlns`
    in the serialized output of the Element Tree.
    """
    for k, v in ns.items():
        ET.register_namespace(k, v)
