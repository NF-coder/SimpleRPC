from pydantic import BaseModel
from typing_extensions import List, Self, Set

class MessageField(BaseModel):
    name: str
    type: str
    isRepeated: bool = False

class Message(BaseModel):
    name: str
    fields: List[MessageField]

    # test this!
    def __eq__(self, value: Self) -> bool: # type: ignore
        return self.name == value.name
    def __ne__(self, value: Self) -> bool: # type: ignore
        return self.name != value.name
    def __hash__(self):
        return hash(self.name)

class Method(BaseModel):
    name: str
    input: str
    output: str

class Service(BaseModel):
    name: str
    methods: List[Method]
    messages: Set[Message]