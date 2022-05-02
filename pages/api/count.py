from asyncio import get_running_loop
from utils import db, count
from fastapi import APIRouter

async def handler(user: int):
    user = str(user)
    if user in db.get("blacklisted", []):
        return {"success": False, "message": "User is blacklisted"}
    if db.get("users", {}).get(user) and (db["users"][user]["counting"] or db["users"][user]["quick_counting"]):
        return {"success": False, "message": "User is already being counted"}
    get_running_loop().create_task(count(user))
    return {"success": True, "message": "Started counting"}

def setup(router: APIRouter):
    router.add_api_route(
        path="/count/{user}",
        name="Count without the cursor",
        endpoint=handler,
        methods=["POST"]
    )
