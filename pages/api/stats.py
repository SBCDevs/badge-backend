from fastapi import APIRouter
from utils import db


async def handler():
    users = await db.get_all_users()
    return {
        "success": True,
        "data": {
            "users": len(users),
            "counting": len(
                [
                    user
                    
                    for user in users
                    
                    if (user.counting or user.quick_counting)
                ]
            ),
            "badges": sum(user.count for user in users),
        },
    }


def setup(router: APIRouter):
    router.add_api_route(
        path="/stats", name="Backend Stats", endpoint=handler, methods=["GET"]
    )
