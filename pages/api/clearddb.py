from asyncio import get_running_loop
from utils import db, update_users
__import__("dotenv").load_dotenv()
from fastapi import APIRouter
from datetime import datetime
from models import User
from os import getenv
import json

async def handler(key: str = ""):
    if key != getenv("APIKEY"):
        return {"success": False, "message": "Invalid API key"}

    db_dump = await db.client.select_all(db.USERS_TABLE)
    with open(f"./backups/{datetime.now().strftime('%d-%m-%Y')}.json", "w") as f:
        json.dump(db_dump, f, indent=4)

    database = db_dump.copy()
    users = [User(**user)._id for user in database]

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
