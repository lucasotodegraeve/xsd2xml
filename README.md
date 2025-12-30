# xsd2xml

Use XSD to generate random XML documents.

_Note: This is hobby project. I'm not planning on developing this library any further._

## Usage

```py
import xsd2xml

xml_document = xsd2xml.generate("tests/assets/premis.xsd.xml", "premis")
xml_document.write("premis.xml")
```

## Setup

Install the dependencies

```
uv sync --extra test
```

Run the tests

```
pytest
```

## Motivation
When might this type of generation be usefull? The intial idea was to validate the correctness of python dataclasses for a [work project](https://github.com/viaacode/sipin-eark-models) using some sort of fuzzy testing.

## Possible improvements
It is currently not clear which specific XML element functions in this library expects. E.g. the following function expects a XML node with the tag `xsd:element`. However this function could be called with any XML node without your type checker giving an error.

```py
def generate_element(xsd_element: ET.Element) -> XMLElement: ...
```

I think maintainability would improve if the schema for a XSD document (i.e. the schema of the schema language) were to be moddelled using dataclasses. These dataclasses could then be used to clearly type-hint functions.

```py
class XSDElement: ...

def generate_element(xsd_element: XSDElement) -> XMLElement: ...
```
