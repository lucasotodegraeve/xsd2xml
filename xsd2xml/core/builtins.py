from enum import Enum
import random
import string
from uuid import UUID


class Marker(str): ...


class IDMarker(Marker): ...


class IDREFMarker(Marker): ...


class BuiltIn(str, Enum):
    # https://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes
    string = "xsd:string"
    boolean = "xsd:boolean"
    decimal = "xsd:decimal"
    float = "xsd:float"
    double = "xsd:double"
    duration = "xsd:duration"
    date_time = "xsd:dateTime"
    time = "xsd:time"
    date = "xsd:date"
    g_year_month = "xsd:gYearMonth"
    g_year = "xsd:gYear"
    g_month_day = "xsd:gMonthDay"
    g_day = "xsd:gDay"
    g_month = "xsd:gMonth"
    hex_binary = "xsd:hexBinary"
    base64_binary = "xsd:base64Binary"
    any_uri = "xsd:anyURI"
    q_name = "xsd:QName"
    notation = "xsd:NOTATION"

    # https://www.w3.org/TR/xmlschema-2/#built-in-derived
    normalizedstring = "xsd:normalizedString"
    token = "xsd:token"
    language = "xsd:language"
    nmtoken = "xsd:NMTOKEN"
    nmtokens = "xsd:NMTOKENS"
    xsd_name = "xsd:Name"
    ncname = "xsd:NCName"
    id = "xsd:ID"
    idref = "xsd:IDREF"
    idrefs = "xsd:IDREFS"
    entity = "xsd:ENTITY"
    entities = "xsd:ENTITIES"
    integer = "xsd:integer"
    nonpositiveinteger = "xsd:nonPositiveInteger"
    negativeinteger = "xsd:negativeInteger"
    long = "xsd:long"
    int = "xsd:int"
    short = "xsd:short"
    byte = "xsd:byte"
    nonnegativeinteger = "xsd:nonNegativeInteger"
    unsignedlong = "xsd:unsignedLong"
    unsignedint = "xsd:unsignedInt"
    unsignedshort = "xsd:unsignedShort"
    unsignedbyte = "xsd:unsignedByte"
    positiveinteger = "xsd:positiveInteger"


def uuid4():
    return "uuid-" + str(
        UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)
    )


def random_built_in_type(type: BuiltIn) -> str:
    match type:
        # Primitive types
        case BuiltIn.string:
            return random_string()
        case BuiltIn.boolean:
            return random_boolean()
        case BuiltIn.decimal:
            return random_decimal()
        case BuiltIn.float:
            return random_float()
        case BuiltIn.double:
            return random_double()
        case BuiltIn.duration:
            return random_duration()
        case BuiltIn.date_time:
            raise NotImplementedError()
        case BuiltIn.time:
            raise NotImplementedError()
        case BuiltIn.date:
            raise NotImplementedError()
        case BuiltIn.g_year_month:
            raise NotImplementedError()
        case BuiltIn.g_year:
            raise NotImplementedError()
        case BuiltIn.g_month_day:
            raise NotImplementedError()
        case BuiltIn.g_day:
            raise NotImplementedError()
        case BuiltIn.g_month:
            raise NotImplementedError()
        case BuiltIn.hex_binary:
            raise NotImplementedError()
        case BuiltIn.base64_binary:
            raise NotImplementedError()
        case BuiltIn.any_uri:
            return random_any_uri()
        case BuiltIn.q_name:
            raise NotImplementedError()
        case BuiltIn.notation:
            raise NotImplementedError()

        # Derived types
        case BuiltIn.normalizedstring:
            raise NotImplementedError()
        case BuiltIn.token:
            raise NotImplementedError()
        case BuiltIn.language:
            raise NotImplementedError()
        case BuiltIn.nmtoken:
            raise NotImplementedError()
        case BuiltIn.nmtokens:
            raise NotImplementedError()
        case BuiltIn.xsd_name:
            raise NotImplementedError()
        case BuiltIn.ncname:
            raise NotImplementedError()
        case BuiltIn.id:
            return IDMarker(random_id())
        case BuiltIn.idref:
            return IDREFMarker()
        case BuiltIn.idrefs:
            raise NotImplementedError()
        case BuiltIn.entity:
            raise NotImplementedError()
        case BuiltIn.entities:
            raise NotImplementedError()
        case BuiltIn.integer:
            return random_integer()
        case BuiltIn.nonpositiveinteger:
            raise NotImplementedError()
        case BuiltIn.negativeinteger:
            raise NotImplementedError()
        case BuiltIn.long:
            raise NotImplementedError()
        case BuiltIn.int:
            raise NotImplementedError()
        case BuiltIn.short:
            raise NotImplementedError()
        case BuiltIn.byte:
            raise NotImplementedError()
        case BuiltIn.nonnegativeinteger:
            raise NotImplementedError()
        case BuiltIn.unsignedlong:
            raise NotImplementedError()
        case BuiltIn.unsignedint:
            raise NotImplementedError()
        case BuiltIn.unsignedshort:
            raise NotImplementedError()
        case BuiltIn.unsignedbyte:
            raise NotImplementedError()
        case BuiltIn.positiveinteger:
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


def random_any_uri() -> str:
    # TODO: relative, fragments
    return "https://www.example.com/"


def random_id() -> str:
    return uuid4()
