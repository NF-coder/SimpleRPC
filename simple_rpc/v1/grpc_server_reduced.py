from pydantic import BaseModel
import grpc
from typing_extensions import Callable
import asyncio
import inspect

class GrpcServer():

    # --- CONFIGURATION AND STARTUP PART ---

    def __init__(self, proto_filename: str = "proto.proto") -> None: 
        self.proto_pb2, self.proto_pb2_grpc = grpc.protos_and_services(proto_filename) # type: ignore

    def _register_servicer(self, proto_service_name) -> Callable:
        service_name = f"{proto_service_name}Servicer" # Service grpc pseudonim
        register_class = getattr(
            self.proto_pb2_grpc, service_name
        ) # Grpc service class
        super(register_class) # init grpc service class

        return getattr(
            self.proto_pb2_grpc, f"add_{service_name}_to_server"
        ) # function, that adds class to grpc service class

    def _enable_service(self) -> type[grpc.aio.Server]:
        server = grpc.aio.server() # async serveer init
        server.add_insecure_port(self.adress) # INSECURE connection info

        self._register_servicer(
            self.proto_service_name
        )(self.cls, server) # proto service registration
        return server # type: ignore
    
    def configure_service(
            self,
            cls,
            proto_service_name: str,
            ip: str = "0.0.0.0",
            port: int = 50051
        ) -> None:
        
        self.adress = f"{ip}:{port}"
        self.proto_service_name = proto_service_name
        self.cls = cls

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_async())
        finally:
            loop.close()

    async def run_async(self):
        server = self._enable_service()
        await server.start()
        await server.wait_for_termination()

    # --- MAIN PART ---

    def grpc_method(
            grpc_cls_self, # self alias pylint:disable=reportSelfClsParameterName
            out_proto_name: str, # name of ouptut proto message
            inp_model: type[BaseModel] | None = None, # input pydantic model
            out_model: type[BaseModel] | None = None, # output pydantic model
        ) -> Callable: # megawrapper
        '''
            gRPC decodator initializer

            Args:
                out_proto_name (str):
                    name of ouptut proto message
                inp_model (`Base Model` ?):
                    input pydantic model
                out_model (`Base Model` ?):
                    output pydantic model
            Returns:
                Callable:
                    wrapped function
        '''
        def wrap_grpc_serv(func) -> Callable: # wrapper
            '''
                gRPC decorator

                Args:
                    func (`Callable`):
                        function
                Returns:
                    Callable:
                        wrapped function
            '''
            async def wrapper(self, request: object, context: grpc.aio.ServicerContext):
                '''
                    gRPC wrapper

                    Args:
                        request:
                            gRPC parsed message
                        context (grpc.aio.ServicerContext):
                            gRPC context
                    Returns:
                        object:
                            gRPC parsed message
                '''
                try:
                    if inp_model is not None:
                        func_kwargs = inp_model.model_validate(
                            request,
                            from_attributes=True
                        ).model_dump()
                    else: # TODO: REWRITE THIS!
                        func_kwargs = {
                            k: request.__getattribute__(k)
                            for k in inspect.signature(func).parameters.keys()
                            if k != "self"
                        }
                    
                    _ = await func(self, **func_kwargs)

                    if out_model is not None: # optional
                        if not isinstance(_, out_model):  # TODO: test this
                            raise ValueError("responce model type mismatch")

                    out_proto = getattr(
                        grpc_cls_self.proto_pb2, out_proto_name
                    )
                    return out_proto(**_.model_dump())
                except Exception as exc:
                    await context.abort(
                        code=grpc.StatusCode.INTERNAL,
                        details=f"{exc.__class__.__name__}: {exc.__str__()}"
                    )
            return wrapper
        return wrap_grpc_serv
