import grpc
from typing_extensions import Callable
import asyncio
import pathlib
import sys
import os

from .proto_builder.proto_builder import ProtoBuilder

class GrpcServer():

    # --- CONFIGURATION AND STARTUP PART ---

    def __init__(self) -> None: 
        self.proto_builder = ProtoBuilder()

    def _register_servicer(self, proto_service_name) -> Callable:
        return getattr(
            self.proto_pb2_grpc, f"add_{proto_service_name}Servicer_to_server"
        ) # function, that adds class to grpc service class

    def _create_server_template(self) -> type[grpc.aio.Server]:
        server = grpc.aio.server() # async serveer init
        server.add_insecure_port(self.adress) # INSECURE connection info

        self._register_servicer(
            self.cls.__class__.__name__
        )(self.cls, server) # proto service registration
        
        return server # type: ignore
    
    def configure_service(
            self,
            cls,
            proto_file_relpath: str = None, # type: ignore
            ip: str = "0.0.0.0",
            port: int = 50051,
        ) -> None:
        
        self.adress = f"{ip}:{port}"
        self.cls = cls

        self.proto_file_relapath = proto_file_relpath
        self.relpath = pathlib.Path("simplerpc_tmp")   
        self.abspath = pathlib.Path(os.path.realpath(sys.argv[0])).parent / self.relpath
        self.abspath.mkdir(parents=True, exist_ok=True)

    def build_proto_file(self):
        path = pathlib.Path.joinpath(self.abspath, f"{self.cls.__class__.__name__}.proto")

        with open(path, "w+", encoding="utf-8-sig") as f:
            f.write(
                self.proto_builder.build(
                    cls = self.cls
                )
            )
        return pathlib.Path.joinpath(self.relpath, f"{self.cls.__class__.__name__}.proto")

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_async())
        finally:
            loop.close()

    async def run_async(self):
        if self.proto_file_relapath is None:
            self.proto_file_relapath = self.build_proto_file()

        self.proto_pb2, self.proto_pb2_grpc = grpc.protos_and_services(
            self.proto_file_relapath.__str__()
        ) # type: ignore

        server = self._create_server_template()
        await server.start() # type: ignore
        await server.wait_for_termination() # type: ignore

    # --- MAIN PART ---

    def grpc_method(
            grpc_cls_self, # self alias # type: ignore
        ) -> Callable:
        def wrap_grpc_serv(func) -> Callable: # wrapper
            grpc_cls_self.proto_builder.add_grpc_model(
                func
            )
            async def wrapper(self, request: object, context: grpc.aio.ServicerContext):
                try:
                    req_model = func.__annotations__["request"].model_validate(
                        request,
                        from_attributes=True
                    )
                    
                    func_result = await func(
                        self, 
                        request=req_model
                    )

                    out_proto = getattr(
                        grpc_cls_self.proto_pb2, f"{func.__name__}Responce"
                    )
                    return out_proto(**func_result.model_dump())
                except Exception as exc:
                    await context.abort(
                        code=grpc.StatusCode.INTERNAL,
                        details=f"{exc.__class__.__name__}: {exc.__str__()}"
                    )
            return wrapper
        return wrap_grpc_serv
