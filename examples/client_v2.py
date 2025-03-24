from pydantic import BaseModel
from simple_rpc import GrpcClient
import asyncio

client = GrpcClient(
    proto_file_relpath="simplerpc_tmp/Server.proto",
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