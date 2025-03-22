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