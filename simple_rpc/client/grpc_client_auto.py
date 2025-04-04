import grpc
from .exceptions import GRPCException

import pathlib
import os
import sys

class Command():
    def __init__(
            self,
            proto_pb2: object,
            proto_pb2_grpc: object,
            ip: str,
            port: int,
            struct_name: str,
            func_name: str,
            service_name: str
        ):
        self.proto_pb2 = proto_pb2
        self.proto_pb2_grpc = proto_pb2_grpc
        self.ip = ip
        self.port = port
        self.struct_name = struct_name
        self.func_name = func_name
        self.service_name = service_name

    async def __call__(self, *args, **kwargs):
        async with grpc.aio.insecure_channel(f"{self.ip}:{self.port}") as channel:
            stub = getattr(
                self.proto_pb2_grpc, f"{self.service_name}Stub"
            )(channel=channel)
            try:
                _ = getattr(
                    self.proto_pb2, self.struct_name
                )(*args, **kwargs) # request structure setter

                response = await getattr(
                   stub, self.func_name
                )(_) # responce getter

                return response
            except grpc.aio.AioRpcError as rpc_error:
                # print(rpc_error.details())
                raise GRPCException(rpc_error.details())

class GrpcClient():
    def __init__(
            self,
            proto_file_relpath: str, # type: ignore
            ip: str = "0.0.0.0",
            port: int = 50051
        ) -> None:

        self.ip = ip
        self.port = port
        
        self.proto_pb2, self.proto_pb2_grpc = grpc.protos_and_services(
            proto_file_relpath
        ) # type: ignore

    def configure_command(
            self,
            functionName: str,
            className: str
        ) -> Command:
        return Command(
            proto_pb2 = self.proto_pb2,
            proto_pb2_grpc = self.proto_pb2_grpc,
            ip = self.ip,
            port = self.port,
            struct_name = f"{functionName}Request",
            func_name = functionName,
            service_name = className
        )
