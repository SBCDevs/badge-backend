from utils import db, save_db, backup_db, update_users
from asyncio import get_running_loop

__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from os import getenv


async def handler(key: str = None):
    if key != getenv("apikey"):
        return {"success": False, "message": "Invalid API key"}
    backup_db()
    users = list(db["users"].keys())
    db["users"] = {}
    save_db()
    get_running_loop().create_task(update_users(users=users))
    return {
        "success": True,
        "message": "Successfully reset the whole database and started recounting everyone.",
    }


def setup(router: APIRouter):
    router.add_api_route(
        path="/cleardb", name="Reset the database", endpoint=handler, methods=["DELETE"]
    )
    router.add_api_route(
        path="/cleardb",
        name="Reset the database",
        endpoint=handler,
        methods=["GET"],
        include_in_schema=False,
    )
