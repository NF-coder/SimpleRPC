from dataclasses import dataclass

@dataclass
class GRPCException(Exception):
    details: str | None