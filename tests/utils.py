import io
import xml.etree.ElementTree as ET
import random


def set_seed(i: int):
    random.seed(i)


def serialize_tree(tree: ET.ElementTree) -> str:
    data = io.StringIO()
    ET.indent(tree)
    tree.write(data, encoding="unicode")
    print(data.getvalue())
    return data.getvalue()
