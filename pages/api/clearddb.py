from utils import db, save_db, count, update_db
from asyncio import get_running_loop, gather
__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv

async def handler(key: str = None):
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    save_db(db_file="db.backup.json")
    users = list(db["users"].keys())
    db["users"] = {}
    save_db()
    tasks = (count(user) for user in users)
    get_running_loop().create_task(gather(*tasks))
    get_running_loop().create_task(update_db())
    return {"success": True, "message": "Successfully reset the whole database and started recounting everyone."}

def setup(router: APIRouter):
    router.add_api_route(
        path="/cleardb",
        name="Reset the database",
        endpoint=handler,
        methods=["DELETE"]
    )
