from pydantic import BaseModel
import grpc
from .exceptions import GRPCException

class Command():
    def __init__(
            self,
            proto_pb2: object,
            proto_pb2_grpc: object,
            ip: str,
            port: int,
            struct_name: str,
            func_name: str,
            service_name: str,
            responce_validation_model: type[BaseModel] | None = None
        ):
        self.proto_pb2 = proto_pb2
        self.proto_pb2_grpc = proto_pb2_grpc
        self.ip = ip
        self.port = port
        self.struct_name = struct_name
        self.func_name = func_name
        self.service_name = service_name
        self.responce_validation_model = responce_validation_model

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

                if self.responce_validation_model is not None:
                    return self.responce_validation_model.model_validate(
                        response,
                        from_attributes=True
                    )

                return response
            except grpc.aio.AioRpcError as rpc_error:
                print(rpc_error.details())
                raise GRPCException(rpc_error.details())

class GrpcClient():
    def __init__(
            self,
            proto_filename: str = "proto.proto",
            ip: str = "0.0.0.0",
            port: int = 50051
        ) -> None: 
        self.proto_pb2, self.proto_pb2_grpc = grpc.protos_and_services(proto_filename) # type: ignore
        self.ip = ip
        self.port = port
    
    def configure_command(
            self,
            struct_name: str,
            func_name: str,
            service_name: str,
            responce_validation_model: type[BaseModel] | None = None
        ) -> Command:
        return Command(
            proto_pb2 = self.proto_pb2,
            proto_pb2_grpc = self.proto_pb2_grpc,
            ip = self.ip,
            port = self.port,
            struct_name = struct_name,
            func_name = func_name,
            service_name = service_name,
            responce_validation_model = responce_validation_model
        )
