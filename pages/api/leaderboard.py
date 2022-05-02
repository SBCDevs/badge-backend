from utils import reorder_leaderboard
from fastapi import APIRouter

async def handler():
    return {"success": True, "data": await reorder_leaderboard()}

def setup(router: APIRouter):
    router.add_api_route(
        path="/leaderboard",
        name="Leaderboard",
        endpoint=handler,
        methods=["GET"]
    )
