from utils import save_db, logger
from fastapi import APIRouter


async def handler():
    try: save_db()
    except Exception as e: logger.log_traceback(error=e)

def setup(router: APIRouter):
    router.add_event_handler("startup", handler)
