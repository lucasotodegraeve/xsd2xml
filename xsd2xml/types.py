from enum import Enum
import random
import string
from dataclasses import dataclass
from uuid import UUID

from lxml.etree import _Element  # type: ignore


@dataclass
class ComplexType:
    root: _Element


@dataclass
class SimpleType:
    root: _Element


class BuiltInType(str, Enum):
    # https://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes
    string = "{http://www.w3.org/2001/XMLSchema}string"
    boolean = "{http://www.w3.org/2001/XMLSchema}boolean"
    decimal = "{http://www.w3.org/2001/XMLSchema}decimal"
    float = "{http://www.w3.org/2001/XMLSchema}float"
    double = "{http://www.w3.org/2001/XMLSchema}double"
    duration = "{http://www.w3.org/2001/XMLSchema}duration"
    date_time = "{http://www.w3.org/2001/XMLSchema}dateTime"
    time = "{http://www.w3.org/2001/XMLSchema}time"
    date = "{http://www.w3.org/2001/XMLSchema}date"
    g_year_month = "{http://www.w3.org/2001/XMLSchema}gYearMonth"
    g_year = "{http://www.w3.org/2001/XMLSchema}gYear"
    g_month_day = "{http://www.w3.org/2001/XMLSchema}gMonthDay"
    g_day = "{http://www.w3.org/2001/XMLSchema}gDay"
    g_month = "{http://www.w3.org/2001/XMLSchema}gMonth"
    hex_binary = "{http://www.w3.org/2001/XMLSchema}hexBinary"
    base64_binary = "{http://www.w3.org/2001/XMLSchema}base64Binary"
    any_uri = "{http://www.w3.org/2001/XMLSchema}anyURI"
    q_name = "{http://www.w3.org/2001/XMLSchema}QName"
    notation = "{http://www.w3.org/2001/XMLSchema}NOTATION"

    # https://www.w3.org/TR/xmlschema-2/#built-in-derived
    normalizedstring = "{http://www.w3.org/2001/XMLSchema}normalizedString"
    token = "{http://www.w3.org/2001/XMLSchema}token"
    language = "{http://www.w3.org/2001/XMLSchema}language"
    nmtoken = "{http://www.w3.org/2001/XMLSchema}NMTOKEN"
    nmtokens = "{http://www.w3.org/2001/XMLSchema}NMTOKENS"
    xsd_name = "{http://www.w3.org/2001/XMLSchema}Name"
    ncname = "{http://www.w3.org/2001/XMLSchema}NCName"
    id = "{http://www.w3.org/2001/XMLSchema}ID"
    idref = "{http://www.w3.org/2001/XMLSchema}IDREF"
    idrefs = "{http://www.w3.org/2001/XMLSchema}IDREFS"
    entity = "{http://www.w3.org/2001/XMLSchema}ENTITY"
    entities = "{http://www.w3.org/2001/XMLSchema}ENTITIES"
    integer = "{http://www.w3.org/2001/XMLSchema}integer"
    nonpositiveinteger = "{http://www.w3.org/2001/XMLSchema}nonPositiveInteger"
    negativeinteger = "{http://www.w3.org/2001/XMLSchema}negativeInteger"
    long = "{http://www.w3.org/2001/XMLSchema}long"
    int = "{http://www.w3.org/2001/XMLSchema}int"
    short = "{http://www.w3.org/2001/XMLSchema}short"
    byte = "{http://www.w3.org/2001/XMLSchema}byte"
    nonnegativeinteger = "{http://www.w3.org/2001/XMLSchema}nonNegativeInteger"
    unsignedlong = "{http://www.w3.org/2001/XMLSchema}unsignedLong"
    unsignedint = "{http://www.w3.org/2001/XMLSchema}unsignedInt"
    unsignedshort = "{http://www.w3.org/2001/XMLSchema}unsignedShort"
    unsignedbyte = "{http://www.w3.org/2001/XMLSchema}unsignedByte"
    positiveinteger = "{http://www.w3.org/2001/XMLSchema}positiveInteger"


def uuid4():
    return "uuid-" + str(
        UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)
    )


def random_build_in_type(type: BuiltInType) -> str:
    match type:
        # Primitive types
        case BuiltInType.string:
            return random_string()
        case BuiltInType.boolean:
            return random_boolean()
        case BuiltInType.decimal:
            return random_decimal()
        case BuiltInType.float:
            return random_float()
        case BuiltInType.double:
            return random_double()
        case BuiltInType.duration:
            return random_duration()
        case BuiltInType.date_time:
            raise NotImplementedError()
        case BuiltInType.time:
            raise NotImplementedError()
        case BuiltInType.date:
            raise NotImplementedError()
        case BuiltInType.g_year_month:
            raise NotImplementedError()
        case BuiltInType.g_year:
            raise NotImplementedError()
        case BuiltInType.g_month_day:
            raise NotImplementedError()
        case BuiltInType.g_day:
            raise NotImplementedError()
        case BuiltInType.g_month:
            raise NotImplementedError()
        case BuiltInType.hex_binary:
            raise NotImplementedError()
        case BuiltInType.base64_binary:
            raise NotImplementedError()
        case BuiltInType.any_uri:
            raise NotImplementedError()
        case BuiltInType.q_name:
            raise NotImplementedError()
        case BuiltInType.notation:
            raise NotImplementedError()

        # Derived types
        case BuiltInType.normalizedstring:
            raise NotImplementedError()
        case BuiltInType.token:
            raise NotImplementedError()
        case BuiltInType.language:
            raise NotImplementedError()
        case BuiltInType.nmtoken:
            raise NotImplementedError()
        case BuiltInType.nmtokens:
            raise NotImplementedError()
        case BuiltInType.xsd_name:
            raise NotImplementedError()
        case BuiltInType.ncname:
            raise NotImplementedError()
        case BuiltInType.id:
            return uuid4()
        case BuiltInType.idref:
            raise NotImplementedError()
        case BuiltInType.idrefs:
            raise NotImplementedError()
        case BuiltInType.entity:
            raise NotImplementedError()
        case BuiltInType.entities:
            raise NotImplementedError()
        case BuiltInType.integer:
            return random_integer()
        case BuiltInType.nonpositiveinteger:
            raise NotImplementedError()
        case BuiltInType.negativeinteger:
            raise NotImplementedError()
        case BuiltInType.long:
            raise NotImplementedError()
        case BuiltInType.int:
            raise NotImplementedError()
        case BuiltInType.short:
            raise NotImplementedError()
        case BuiltInType.byte:
            raise NotImplementedError()
        case BuiltInType.nonnegativeinteger:
            raise NotImplementedError()
        case BuiltInType.unsignedlong:
            raise NotImplementedError()
        case BuiltInType.unsignedint:
            raise NotImplementedError()
        case BuiltInType.unsignedshort:
            raise NotImplementedError()
        case BuiltInType.unsignedbyte:
            raise NotImplementedError()
        case BuiltInType.positiveinteger:
            raise NotImplementedError()


def random_string() -> str:
    return "".join(random.choices(string.ascii_letters, k=10))


def random_boolean() -> str:
    boolean = random.random() > 0.5
    match boolean:
        case True:
            return "true"
        case False:
            return "false"


def random_float() -> str:
    return str(random.uniform(-100, 100))


def random_double() -> str:
    mantissa = random_decimal()
    exponent = random_integer()
    choices = [
        "INF",
        "-INF",
        "NaN",
        "NaN",
        "-0",
        f"{mantissa}e{exponent}",
        f"{mantissa}E{exponent}",
        f"{mantissa}",
    ]
    return random.choices(choices, weights=[1, 1, 1, 1, 1, 10, 10, 10], k=1)[0]


def random_decimal() -> str:
    integer_part = random_integer()
    fractional_part = random.randint(0, 100)
    choices = [
        integer_part,
        f"{integer_part}.",
        f"{integer_part}.00",
        f"{integer_part}.{fractional_part}",
    ]
    return random.choice(choices)


def random_integer() -> str:
    value = random.randint(-100, 100)
    choices = [str(value)]
    if value > 0:
        choices.append(f"+{value}")
    return random.choice(choices)


def random_duration() -> str:
    years = random.randint(0, 10)
    months = random.randint(0, 10)
    days = random.randint(0, 10)
    hours = random.randint(0, 10)
    minutes = random.randint(0, 10)
    seconds_integer = random.randint(0, 100)
    seconds_fraction = random.randint(0, 100)
    seconds = random.choice(
        [
            f"{seconds_integer}.{seconds_fraction}",
            f"{seconds_integer}",
        ]
    )

    sign = random.choice(["-", ""])
    years_str = random.choice([f"{years}Y", "0Y", ""])
    months_str = random.choice([f"{months}M", "0M", ""])
    days_str = random.choice([f"{days}D", "0D", ""])

    hours_str = random.choice([f"{hours}H", "0H", ""])
    minutes_str = random.choice([f"{minutes}M", "0M", ""])
    seconds_str = random.choice([f"{seconds}S", "0S", ""])

    T_designator = "T"
    if hours_str == "" and minutes_str == "" and seconds_str == "":
        T_designator = ""

    duration = f"{sign}P{years_str}{months_str}{days_str}{T_designator}{hours_str}{minutes_str}{seconds_str}"
    if T_designator == "" and years_str == "" and months_str == "" and days_str == "":
        duration = f"{sign}P0Y"

    choices = [
        "P0Y0M0DT0H0M0S",
        "P0Y0M0D",
        "-P0Y0M0DT0H0M0S",
        "P0Y0M0DT0H0M0.00S",
        duration,
    ]
    return random.choices(choices, weights=[1, 1, 1, 1, 10], k=1)[0]
