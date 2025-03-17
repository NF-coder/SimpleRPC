from pydantic import BaseModel
from simple_rpc_future import GrpcClient
import asyncio

class ResponceModel(BaseModel):
    num2: int
    num4: int

cli = GrpcClient(
    port=50056
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