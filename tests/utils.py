import io
import xml.etree.ElementTree as ET


def serialize_tree(tree: ET.ElementTree) -> str:
    data = io.StringIO()
    tree.write(data, encoding="unicode")
    return data.getvalue()
