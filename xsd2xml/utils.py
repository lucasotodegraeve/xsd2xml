ns = {"xsd": "http://www.w3.org/2001/XMLSchema"}


class InvalidXSDError(Exception): ...


def _expand_qname(qname: str | None, nsmap: dict[str | None, str]) -> str | None:
    if qname is None:
        return None
    if ":" not in qname:
        return qname
    if len(qname) > 0 and qname[0] == "{":
        return None
    idx = qname.find(":")
    return "{" + nsmap[qname[:idx]] + "}" + qname[idx + 1 :]
