from utils import db, save_db, reorder_leaderboard

__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv


async def handler(user: int, key: str = None):
    user = str(user)
    if key != getenv("apikey"):
        return {"success": False, "message": "Invalid API key"}
    if user not in db.get("blacklisted", []):
        return {"success": False, "message": "User not blacklisted"}
    db["blacklisted"].remove(user)
    save_db()
    await reorder_leaderboard()
    return {"success": True, "message": "User unblacklisted"}


def setup(router: APIRouter):
    router.add_api_route(
        path="/unblacklist/{user}",
        name="Unblacklist a user",
        endpoint=handler,
        methods=["DELETE"],
    )
    router.add_api_route(
        path="/unblacklist/{user}",
        name="Unblacklist a user",
        endpoint=handler,
        methods=["GET"],
        include_in_schema=False,
    )
