from fastapi import APIRouter
from utils import db


async def handler():
    return {
        "success": True,
        "data": {
            "users": len(db.get("users", {})),
            "counting": len(
                [
                    i
                    for i in db.get("users", {})
                    if (
                        db["users"][i].get("counting", False)
                        or db["users"][i].get("quick_counting", False)
                    )
                ]
            ),
            "badges": sum(db["users"][i].get("count", 0) for i in db.get("users", {})),
        },
    }


def setup(router: APIRouter):
    router.add_api_route(
        path="/stats", name="Backend Stats", endpoint=handler, methods=["GET"]
    )
