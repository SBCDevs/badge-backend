from aiohttp import ClientSession
from fastapi import APIRouter
from utils import logger, format_date


async def handler(user: int):
    user = str(user)
    async with ClientSession() as session:
        try:
            async with session.get(
                f"https://badges.roblox.com/v1/users/{user}/badges?limit=10&sortOrder=Desc"
            ) as resp:
                response = await resp.json()
            d = None
            if next(iter(response["data"] or []), None):
                d = {
                    i: (
                        format_date(response["data"][0][i])
                        if i in ("created", "updated")
                        else response["data"][0][i]
                    )
                    for i in response["data"][0]
                }
                async with session.get(
                    f'https://badges.roblox.com/v1/users/{user}/badges/awarded-dates?badgeIds={d["id"]}'
                ) as resp:
                    response = await resp.json()
                d["awardedDate"] = format_date(response["data"][0]["awardedDate"])
        except Exception as e:
            logger.log_traceback(error=e)
            return {"success": False, "message": "Error whilst fetching badge data"}
    return {"success": True, "data": d}


def setup(router: APIRouter):
    router.add_api_route(
        path="/last/{user}", name="User's last badge", endpoint=handler, methods=["GET"]
    )
