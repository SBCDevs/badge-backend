from utils import db, save_db, reorder_leaderboard
from contextlib import suppress

__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv


async def handler(user: int, key: str = None):
    user = str(user)
    if key != getenv("APIKEY"):
        return {"success": False, "message": "Invalid API key"}
    if not db.get("users", {}).get(user):
        return {"success": False, "message": "User not found"}
    with suppress(KeyError):
        del db["users"][user]["count"]
        del db["users"][user]["cursor_count"]
        del db["users"][user]["cursor"]
    db["users"][user]["counting"] = False
    save_db()
    await reorder_leaderboard()
    return {"success": True, "message": f"Badges cleared for {user}"}


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
