from asyncio import Semaphore
from typing import Coroutine

async def semaphore_wrapper(coroutine: Coroutine, semaphore: Semaphore):
    async with semaphore:
        await coroutine
