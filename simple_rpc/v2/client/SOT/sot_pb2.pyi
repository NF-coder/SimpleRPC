from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class get_active_protoResponce(_message.Message):
    __slots__ = ("proto",)
    PROTO_FIELD_NUMBER: _ClassVar[int]
    proto: str
    def __init__(self, proto: _Optional[str] = ...) -> None: ...

class get_active_protoRquest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
