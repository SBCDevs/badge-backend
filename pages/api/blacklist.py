from utils import db, save_db, reorder_leaderboard

__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv


async def handler(user: int, key: str = None):
    user = str(user)
    if key != getenv("APIKEY"):
        return {"success": False, "message": "Invalid API key"}
    if user in db.get("blacklisted", []):
        return {"success": False, "message": "User already blacklisted"}
    if db.get("users", {}).get(user):
        del db["users"][user]
    db["blacklisted"].append(user)
    save_db()
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
