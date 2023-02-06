from asyncio import get_running_loop
from utils import db, quickcount
from fastapi import APIRouter


async def handler(user: int):
    user_id = str(user)

    u = await db.get_user(user_id)

    if u.blacklisted:
        return {"success": False, "message": "User is blacklisted"}

    if u.counting or u.quick_counting:
        return {"success": False, "message": "User is already being counted"}

    get_running_loop().create_task(quickcount(user_id))

    return {"success": True, "message": "Started quick counting"}


def setup(router: APIRouter):
    router.add_api_route(
        path="/quickcount/{user}",
        name="Count with the cursor",
        endpoint=handler,
        methods=["POST"],
    )
    router.add_api_route(
        path="/quickcount/{user}",
        name="Count with the cursor",
        endpoint=handler,
        methods=["GET"],
        include_in_schema=False,
    )
