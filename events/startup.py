from utils import db, reorder_leaderboard, update_db, logger
from asyncio import get_running_loop
from fastapi import APIRouter


async def handler():
    try:
        for user in db["users"]:
            db["users"][user]["counting"] = False
            db["users"][user]["quick_counting"] = False
        get_running_loop().create_task(reorder_leaderboard())
        get_running_loop().create_task(update_db())
    except Exception as e:
        logger.log_traceback(error=e)


def setup(router: APIRouter):
    router.add_event_handler("startup", handler)
