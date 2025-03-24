from simple_rpc import GrpcServer
from pydantic import BaseModel

class RequestModel(BaseModel):
    pass

class ResponceModel(BaseModel):
    num2: int
    num4: int

app = GrpcServer()

class Server:
    @app.grpc_method()
    async def example_method(self, request: RequestModel) -> ResponceModel:
        return ResponceModel(
            num2 = 3,
            num4 = 1
        )
    
app.configure_service(
    cls=Server(),
    port=50051
)
app.run()