# SimpleRPC

Simple framework to create your own gRPC server with grpcio.

### Installation
```bash
pip install git+https://github.com/NF-coder/SimpleRPC.git
```

### Todo

- [x] Exceptions handling
- [ ] Secure channels support
- [x] Autoconfigure from pydantic model
- [ ] Source-of-truth for protos
- [ ] Tests and docs

## Quick Start

server.py
```python
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
```

client.py
```python
from pydantic import BaseModel
from simple_rpc import GrpcClient
import asyncio

client = GrpcClient(
    proto_file_relpath="simplerpc_tmp/Server.proto", # Generates automatically on server startup
    port=50051
)
command = client.configure_command(
    functionName="example_method",
    className="Server"
)

async def run():
    print(
        await command()
    )

if __name__ == "__main__":
    asyncio.run(
        run()
    )
```
