from fastapi import APIRouter
from utils import db


async def handler():
    return {
        "success": True,
        "data": {
            "users": len(await db.client.select_all(db.USERS_TABLE)),
            "counting": len(
                [
                    i
                    
                    for i in await db.client.select_all(db.USERS_TABLE)
                    
                    if (
                        i.get("counting", False)
                        or i.get("quick_counting", False)
                    )
                ]
            ),
            "badges": sum(i.get("count", 0) for i in (await db.client.select_all(db.USERS_TABLE))),
        },
    }


def setup(router: APIRouter):
    router.add_api_route(
        path="/stats", name="Backend Stats", endpoint=handler, methods=["GET"]
    )
