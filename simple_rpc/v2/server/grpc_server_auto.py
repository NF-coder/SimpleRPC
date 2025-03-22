import grpc
from typing_extensions import Callable
import asyncio
import pathlib
import sys
import os

from .proto_builder.proto_builder import ProtoBuilder
from .SOT.source_of_truth_server import SOTServer

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
        
        self._register_servicer(
            "SOTServer"
        )(
            SOTServer(
                self.autobuilded_proto.split("service SOTServer")[0],
                self.proto_pb2_grpc,
                self.proto_pb2
            ),
            server
        ) # source-of-truth service registration
        
        return server # type: ignore
    
    def configure_service(
            self,
            cls,
            proto_dir_relpath: pathlib.Path = None, # type: ignore
            ip: str = "0.0.0.0",
            port: int = 50051,
        ) -> None:
        if proto_dir_relpath is None:
            proto_dir_relpath=pathlib.Path("simplerpc_server_tmp")
        
        self.adress = f"{ip}:{port}"
        self.cls = cls

        path = pathlib.Path(os.path.realpath(sys.argv[0])).parent / proto_dir_relpath
        path.mkdir(parents=True, exist_ok=True)
        self.abspath = path
        self.relpath = proto_dir_relpath

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_async())
        finally:
            loop.close()

    async def run_async(self):
        path = pathlib.Path.joinpath(self.abspath, f"{self.cls.__class__.__name__}.proto")

        self.autobuilded_proto = self.proto_builder.build(
            cls = self.cls
        )
        with open(path, "w+", encoding="utf-8-sig") as f:
            f.write(
                self.autobuilded_proto
            )
        self.proto_pb2, self.proto_pb2_grpc = grpc.protos_and_services(
            (self.relpath / f"{self.cls.__class__.__name__}.proto").__str__()
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
