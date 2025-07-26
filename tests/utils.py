import io
import xml.etree.ElementTree as ET
import random


def seed_range(n: int):
    for i in range(n):
        set_seed(i)
        yield i


def set_seed(i: int):
    random.seed(i)


def serialize_tree(tree: ET.ElementTree) -> str:
    data = io.StringIO()
    ET.indent(tree)
    tree.write(data, encoding="unicode")
    return data.getvalue()
