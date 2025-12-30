# xsd2xml

Use XSD to generate random XML documents.

_Note: This is a hobby project. I'm not planning on developing this library any further._

## Usage

```py
import xsd2xml

xml_document = xsd2xml.generate("tests/assets/premis.xsd.xml", "premis")
xml_document.write("premis.xml")
```

And out comes an XML document

```xml
<premis:premis>
  <!-- ... -->
</premis:premis>
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
When might this type of generation be useful? The initial idea was to validate the correctness of Python dataclasses for a [work project](https://github.com/viaacode/sipin-eark-models) using some sort of fuzzy testing.

## Possible improvements
It is currently not clear which specific XML node functions expects. E.g. the following function expects an XML node with the tag `xsd:element`. However, this function could be called with any XML node without your type checker giving an error.

```py
def generate_element(xsd_element: ET.Element) -> XMLElement: ...
```

I think maintainability would improve if the schema for an XSD document (i.e. the schema of the schema language) were to be modelled using dataclasses. These dataclasses could then be used to clearly type-hint functions.

```py
class XSDElement: ...

def generate_element(xsd_element: XSDElement) -> XMLElement: ...
```
