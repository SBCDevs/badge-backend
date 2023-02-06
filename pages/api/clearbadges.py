from utils import db, reorder_leaderboard
from contextlib import suppress

__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv


async def handler(user: int, key: str = ""):
    user_id = str(user)
    
    if key != getenv("APIKEY"):
        return {"success": False, "message": "Invalid API key"}
    
    await db.update_user(user_id, {
        "cursor": None,
        "cursor_count": 0,
        "count": 0,
        "counting": False,
        "quick_counting": False
    })
    
    await reorder_leaderboard()
    
    return {"success": True, "message": f"Badges cleared for {user_id}"}


def setup(router: APIRouter):
    router.add_api_route(
        path="/clearbadges/{user}",
        name="Clear badges of a user",
        endpoint=handler,
        methods=["DELETE"],
    )
    router.add_api_route(
        path="/clearbadges/{user}",
        name="Clear badges of a user",
        endpoint=handler,
        methods=["GET"],
        include_in_schema=False,
    )
