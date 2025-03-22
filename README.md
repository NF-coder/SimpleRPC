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
- [x] Simplify usage
- [ ] Tests and docs

## Quick Start

server.py
```python
from simple_rpc.v2.server import GrpcServerV2
from pydantic import BaseModel

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
    port=50051
)
app.run()
```

client.py
```python
from pydantic import BaseModel
from simple_rpc.v2.client import GrpcClientV2
import asyncio

client = GrpcClientV2(
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
