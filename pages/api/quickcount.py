from asyncio import get_running_loop
from utils import db, quickcount
from fastapi import APIRouter

async def handler(user: int):
    user = str(user)
    if user in db.get("blacklisted", []):
        return {"success": False, "message": "User is blacklisted"}
    if db.get("users", {}).get(user) and (db["users"][user]["counting"] or db["users"][user]["quick_counting"]):
        return {"success": False, "message": "User is already being counted"}
    get_running_loop().create_task(quickcount(user))
    return {"success": True, "message": "Started quick counting"}

def setup(router: APIRouter):
    router.add_api_route(
        path="/quickcount/{user}",
        name="Count with the cursor",
        endpoint=handler,
        methods=["POST"]
    )
    router.add_api_route(
        path="/quickcount/{user}",
        name="Count with the cursor",
        endpoint=handler,
        methods=["GET"],
        include_in_schema=False
    )
