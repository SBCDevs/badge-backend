from utils import db, save_db, reorder_leaderboard
__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv

async def handler(user: int, key: str):
    user = str(user)
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
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
        path="/api/blacklist/{user}",
        name="Blacklist a user",
        endpoint=handler,
        methods=["POST"]
    )