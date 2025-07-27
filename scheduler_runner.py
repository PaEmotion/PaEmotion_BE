# scheduler_runner.py

import asyncio
from scheduler import start_scheduler

async def main():
    start_scheduler()
    while True:
        await asyncio.sleep(3600) 

if __name__ == "__main__":
    asyncio.run(main())
