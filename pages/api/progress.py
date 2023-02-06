from fastapi import APIRouter
from utils import db


async def handler(user: int):
    user_id = str(user)

    u = await db.get_user(user_id)

    return {
        "success": True,
        "data": {
            "quick_counting": u.quick_counting,
            "counting": u.counting,
            "count": u.count
        },
    }


def setup(router: APIRouter):
    router.add_api_route(
        path="/progress/{user}",
        name="User Counting Progress",
        endpoint=handler,
        methods=["GET"],
    )
