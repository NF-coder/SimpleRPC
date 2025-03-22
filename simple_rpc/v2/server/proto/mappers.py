import enum

# see: https://protobuf.dev/programming-guides/proto3/#scalar
class TypeEnum(str, enum.Enum):
    INT32 = "int32"
    UINT32 = "uint32"
    SINT32 = "sint32"
    FIXED32 = "fixed32"
    SFIXED32 = "sfixed32"

    INT64 = "int64"
    UINT64 = "uint64"
    SINT64 = "sint64"
    FIXED64 = "fixed64"
    SFIXED64 = "sfixed64"

    FLOAT = "float"
    DOUBLE = "double"
    
    BOOL = "bool"
    STRING = "string"
    BYTES = "bytes"
    MAP = "map"

# see: https://protobuf.dev/programming-guides/proto3/#scalar
TYPE_MAPPING = {
    int: TypeEnum.INT64,
    float: TypeEnum.DOUBLE,
    bool: TypeEnum.BOOL,
    str: TypeEnum.STRING,
    bytes: TypeEnum.BYTES
}