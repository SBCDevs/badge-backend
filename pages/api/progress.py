from fastapi import APIRouter
from utils import db


async def handler(user: int):
    user = str(user)
    try:
        db["users"][user]
    except KeyError:
        return {"success": False, "message": "User not found"}
    return {
        "success": True,
        "data": {
            "quick_counting": db["users"][user].get("quick_counting", False),
            "counting": db["users"][user].get("counting", False),
            "count": db["users"][user].get("count", 0),
        },
    }


def setup(router: APIRouter):
    router.add_api_route(
        path="/progress/{user}",
        name="User Counting Progress",
        endpoint=handler,
        methods=["GET"],
    )
