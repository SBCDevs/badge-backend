from utils import logger
from fastapi import APIRouter


async def handler():
    ... # Unused.. for now.. (maybe)


def setup(router: APIRouter):
    router.add_event_handler("startup", handler)
