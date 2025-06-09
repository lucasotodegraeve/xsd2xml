import io
import xml.etree.ElementTree as ET


def tree_to_str(tree: ET.ElementTree) -> str:
    data = io.StringIO()
    tree.write(data, encoding="unicode")
    return data.getvalue()
