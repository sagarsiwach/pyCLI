import asyncio
from resource import increase_production_async, increase_storage_async
from config import read_config
from login import login

async def main():
    cookies = await login()
    config = read_config()

    # Loop for increasing production and storage
    while True:
        await increase_production_async(int(config['production_loops']), cookies)
        await increase_storage_async(int(config['storage_loops']), cookies)
        print(f"Production completed: {config['production_completed']}, Storage completed: {config['storage_completed']}")

if __name__ == "__main__":
    asyncio.run(main())