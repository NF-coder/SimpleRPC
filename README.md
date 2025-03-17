# SimpleRPC

Simple framework to create your own gRPC server with grpcio.
### It's early version so api isn't stable!

### Todo

- [x] Exceptions handling
- [ ] Autoconfigure from pydantic model
- [ ] Simplify usage
- [ ] Tests and docs

## Quick Start

server.py
```python
from SimpleRPC import GrpcServer
from pydantic import BaseModel
import asyncio

class RequestModel(BaseModel):
    num1: int

class ResponceModel(BaseModel):
    num2: int
    num4: int

app = GrpcServer(
    proto_filename = "proto.proto"
)

class Server: 
    @app.grpc_method(inp_model=RequestModel, out_model=ResponceModel, out_proto_name="ResponceMsg")
    async def Method(self, num1) -> ResponceModel:
        return ResponceModel(
            num2 = num1*2,
            num4 = 99
        )
    
app.configure_service(
    proto_service_name="Example",
    cls = Server(),
    port=50055
)
app.run()
```

client.py
```python
from pydantic import BaseModel
from SimpleRPC import GrpcClient
import asyncio

class ResponceModel(BaseModel):
    num2: int
    num4: int

cli = GrpcClient(
    port=50055
)
command = cli.configure_command(
    struct_name="RequestMsg",
    func_name="Method",
    service_name="Example",
    responce_validation_model=ResponceModel
)

async def run():
    print(
        await command(num1 = 1)
    )

if __name__ == "__main__":
    asyncio.run(
        run()
    )
```

proto.proto
```protobuf
syntax = "proto3";

service Example {
   rpc Method(RequestMsg) returns (ResponceMsg) {}
}

message RequestMsg {
  int32 num1 = 1;
}

message ResponceMsg {
  int32 num2 = 1;
  int32 num4 = 2;
}
```
