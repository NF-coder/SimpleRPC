from simple_rpc import GrpcServer
from pydantic import BaseModel

class RequestModel(BaseModel):
    num1: int

class ResponceModel(BaseModel):
    num2: int
    num4: int

app = GrpcServer(
    proto_filename = "proto.proto"
)

class Server:
    @app.grpc_method(out_proto_name="ResponceMsg")
    async def Method(self, num1) -> ResponceModel:
        return ResponceModel(
            num2 = num1*2,
            num4 = 99
        )
    
app.configure_service(
    proto_service_name="Example",
    cls = Server(),
    port=50056
)
app.run()