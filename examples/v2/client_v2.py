from pydantic import BaseModel
from v2.client.grpc_client_auto import GrpcClient
import asyncio
import pathlib

client = GrpcClient(
    proto_dir_relpath=pathlib.Path("client_tmp"),
    port=50056
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