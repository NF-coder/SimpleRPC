from pydantic import BaseModel
from simple_rpc import GrpcClientV2
import asyncio
import pathlib

client = GrpcClientV2(
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