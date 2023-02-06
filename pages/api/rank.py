from fastapi import APIRouter
from utils import db, reorder_leaderboard


async def handler(user: int):
    try:
        await reorder_leaderboard()
        user_id = str(user)
        u = await db.get_user(user_id)
        return {"success": True, "rank": u.place}
    except KeyError:
        return {"success": False, "message": "User not found"}


def setup(router: APIRouter):
    router.add_api_route(
        path="/rank/{user}",
        name="User Leaderboard Rank",
        endpoint=handler,
        methods=["GET"],
    )
