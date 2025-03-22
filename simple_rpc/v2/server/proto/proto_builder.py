from pydantic import BaseModel

from types import NoneType, UnionType
from typing_extensions import (
    Iterable,
    Type,
    Union,
    get_origin,
    List,
    Any,
    Callable,
    Tuple
)

import inspect

from .mappers import *
from .models import *

import jinja2
import pathlib

TEMPLATE_DIR_PATH = pathlib.Path(__file__).parent / "templates"
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR_PATH), trim_blocks=True)

def render_proto(service: Service):
    template = JINJA_ENV.get_template("service.proto")
    return template.render(service=service)

class ProtoBuilder():
    def __init__(self) -> None:
        self.methods = []

    def build(self, cls: Callable):
        messages_arr = set()
        methods_arr = []

        for func in self.methods:
            messages_arr.update(
                func["messages"]
            )
            
            methods_arr.append(
                Method(
                    name=func["func_name"],
                    input=func["req_name"],
                    output=func["resp_name"]
                )
            )

        template = JINJA_ENV.get_template("/proto_template.proto")
        return template.render(
            service=Service(
                name=cls.__class__.__name__,
                methods=methods_arr,
                messages=messages_arr
            )
        )

    def add_grpc_model(self, func: Callable) -> None:
        parser = Parser()

        # responce type
        responceName = f"{func.__name__}Responce"
        # check existance
        try:
            responce = func.__annotations__["return"]
        except:
            raise TypeError("Responce type annotation not found!")
        # check type
        if not issubclass(responce, BaseModel): raise TypeError("Only padantic model responce supported!")
        resp_data = parser.get_data_from_model(responce, responceName)
        resp_name =  resp_data.name

        # request type
        requestName = f"{func.__name__}Request"        
        # check existance
        try:
            request = func.__annotations__["request"]
        except:
            raise TypeError("Request type annotation not found!")
        # check type
        if not issubclass(request, BaseModel): raise TypeError("Only padantic model request supported!")
        req_data = parser.get_data_from_model(request, requestName)
        req_name = req_data.name

        self.methods.append(
            {
                "messages": parser.messages,
                "func_name": func.__name__,
                "req_name": req_name,
                "resp_name": resp_name
            }
        )


class Parser:
    def __init__(self) -> None:
        self.messages = []
    
    def _parse_Union(self, name: str, parsed_type: Any) -> MessageField:
        args = list(parsed_type.__args__) # noqa pylint:disable=cannot-access-attribute

        if NoneType in args: args.remove(NoneType)
        if len(args) != 1:
            raise TypeError(
                f"Field '{name}': type '{parsed_type}' must have only one subtype, not {len(args)}. "
                "Tip: None/Optional type ignoring."
            )

        return self._parse_field(
            name,
            args[0],
            True
        )

    def _parse_List(self, name: str, parsed_type: Any) -> MessageField:
        args = parsed_type.__args__ # noqa pylint:disable=cannot-access-attribute

        if len(args) != 1:
            raise TypeError(
                f"Field '{name}': type '{parsed_type}' must have only one subtype, not {len(args)}."
            )
        
        _ =  self._parse_field(name, args[0])
        _.isRepeated = True
        return _

    def _parse_field(self, name: str, type: Any, isIterableSupported: bool = False) -> MessageField:
        if type in TYPE_MAPPING: # Normal types parsing
            return MessageField(
                name=name,
                isRepeated=False,
                type=TYPE_MAPPING[type].value
            )

        elif (origin := get_origin(type)) is not None:
            if origin in (Union, UnionType): # optional and optional analogs parsing
                return self._parse_Union(name, type)
            elif isIterableSupported and issubclass(origin, Iterable):
                return self._parse_List(name, type)
            
            raise TypeError(f"Unsupported type '{type}'.")

        elif inspect.isclass(type) and issubclass(type, BaseModel): # pydantic models
            self.get_data_from_model(type)
            return MessageField(
                name=name,
                isRepeated=False,
                type=type.__name__
            )
        
        else: raise TypeError(f"Unsupported type '{type}'.")

    def get_data_from_model(self, model: Type[BaseModel], forcedName: str = None) -> Message: # type: ignore
        message = Message(
            name = model.__name__ if forcedName is None else forcedName,
            fields=[
                self._parse_field(
                    name,
                    field.annotation,
                    True
                ) for name, field in model.model_fields.items()
            ]
        )
        self.messages.append(message)

        return message

    def get_data_from_dict(self, name: str, model: dict) -> Message:
        message = Message(
            name=name,
            fields=[
                self._parse_field(
                    name,
                    field,
                    True
                ) for name, field in zip(model.keys(), model.values())
            ]
        )
        self.messages.append(message)

        return message