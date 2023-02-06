from utils import db, reorder_leaderboard

__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv


async def handler(user: int, key: str = ""):
    user_id = str(user)

    if key != getenv("APIKEY"):
        return {"success": False, "message": "Invalid API key"}
    
    await db.update_user(user_id, {
        "blacklisted": True
    })
    
    await reorder_leaderboard()
    return {"success": True, "message": "User blacklisted"}


def setup(router: APIRouter):
    router.add_api_route(
        path="/blacklist/{user}",
        name="Blacklist a user",
        endpoint=handler,
        methods=["POST"],
    )
    router.add_api_route(
        path="/blacklist/{user}",
        name="Blacklist a user",
        endpoint=handler,
        methods=["GET"],
        include_in_schema=False,
    )
