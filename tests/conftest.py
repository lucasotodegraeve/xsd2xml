import random
import xml.etree.ElementTree as ET

from tests.utils import seed_range

import pytest

ns = {"xsd": "http://www.w3.org/2001/XMLSchema"}


@pytest.fixture(autouse=True)
def _set_seed():
    random.seed(1)


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--fuzzfactor", action="store", default=1)
    parser.addoption("--seed", action="store", default=0)
    parser.addoption("--write", dest="write", action="store_true", default=False)


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "fuzzy_i" in metafunc.fixturenames:
        fuzz_factor = metafunc.config.getoption("fuzzfactor")
        try:
            fuzz_factor = int(str(fuzz_factor))
        except ValueError:
            fuzz_factor = 1
        n = fuzz_factor * 10
        metafunc.parametrize("fuzzy_i", seed_range(n))


@pytest.fixture(autouse=True, scope="session")
def register_namespaces():
    """
    The namespaces are registered here so that they are used as `xmlns`
    in the serialized output of the Element Tree.
    """
    for k, v in ns.items():
        ET.register_namespace(k, v)
