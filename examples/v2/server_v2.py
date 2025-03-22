from simple_rpc import GrpcServerV2
from pydantic import BaseModel
import pathlib

class RequestModel(BaseModel):
    pass

class ResponceModel(BaseModel):
    num2: int
    num4: int

app = GrpcServerV2()

class Server:
    @app.grpc_method()
    async def example_method(self, request: RequestModel) -> ResponceModel:
        return ResponceModel(
            num2 = 3,
            num4 = 1
        )
    
app.configure_service(
    cls=Server(),
    port=50056,
    proto_dir_relpath=pathlib.Path("server_tmp")
)
app.run()