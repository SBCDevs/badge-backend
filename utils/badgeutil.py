from .data import list_chunks, chunks
from . import database as db

__import__("dotenv").load_dotenv()
from aiohttp import ClientSession
from asyncio import gather
from os import getenv
from .log import logger

chunk_size = int(getenv("CHUNK_SIZE", default=250))


async def reorder_leaderboard():
    try:
        users = dict(
            sorted(
                {
                    i.get("_id"): i.get("count", 0) for i in await db.client.select_all(db.USERS_TABLE)
                }.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )
        lb = []
        for place, userid in enumerate(users, start=1):
            user_id = str(userid)
            user = await db.get_user(user_id)
            lb.append(
                {
                    "place": place,
                    "count": user.count,
                    "userId": userid,
                    "quick_counting": user.quick_counting,
                    "counting": user.counting,
                }
            )
            await db.update_user(user_id, {
                "place": place
            })
        return lb
    except Exception as e:
        logger.log_traceback(error=e)


async def quickcount(user: str):
    try:
        u = await db.get_user(user)
        if u.counting or u.quick_counting:
            return
    
        u.quick_counting = True
        logger.debug(f"[QUICK COUNT] {u}")

        params = {"limit": 100, "sortOrder": "Asc"}
        request_url = f"https://badges.roblox.com/v1/users/{user}/badges"

        if u.cursor:
            params["cursor"] = u.cursor
            u.count = u.cursor_count

        async with ClientSession() as session:
            while True:
                async with session.get(request_url, params=params) as resp:
                    response: dict = await resp.json()
                    u.count += len(response.get("data", []))
                    cursor = response.get("nextPageCursor")
                    logger.debug(
                        f"[QUICK COUNT] [{user}] {len(response.get('data', []))} Cursor: {cursor}"
                    )
                if cursor:
                    params["cursor"] = cursor
                    u.cursor_count = u.count
                    u.cursor = cursor
                else:
                    u.quick_counting = False
                    u.counting = False
                    break
        await db.update_user(user, u)
        await reorder_leaderboard()
    except Exception as e:
        logger.log_traceback(error=e)


async def count(user: str):
    try:
        u = await db.get_user(user)
        if u.counting or u.quick_counting:
            return
        
        u.counting = True
        logger.debug(f"[SLOW COUNT] {u}")

        params = {"limit": 100, "sortOrder": "Asc"}
        request_url = f"https://badges.roblox.com/v1/users/{user}/badges"
        cursor_count = 0
        user_badge_count = 0
        current_cursor = None
        cursor = None
        async with ClientSession() as session:
            while True:
                async with session.get(request_url, params=params) as resp:
                    response: dict = await resp.json()
                    cursor_count = user_badge_count
                    user_badge_count += len(response.get("data", []))
                    current_cursor = response.get("nextPageCursor")
                    logger.debug(
                        f"[SLOW COUNT] [{user}] {len(response.get('data', []))} Cursor: {cursor}"
                    )
                if current_cursor:
                    cursor = current_cursor
                    params["cursor"] = current_cursor
                else:
                    u.quick_counting = False
                    u.counting = False
                    u.cursor = cursor
                    u.count = user_badge_count
                    u.cursor_count = cursor_count
                    break
        await reorder_leaderboard()
    except Exception as e:
        logger.log_traceback(error=e)


async def update_db():
    #TODO
    try:
        logger.debug("[STORAGE] Updating database...")
        users = await db.client.select_all(db.USERS_TABLE)
        for chunk in chunks(users, chunk_size):
            tasks = (count(user) for user in chunk)
            await gather(*tasks)
        logger.debug("[STORAGE] Database updated")
    except Exception as e:
        logger.log_traceback(error=e)


async def update_users(users: list):
    #TODO
    try:
        logger.debug(f"[STORAGE] Updating database with {len(users)}...")
        for chunk in list_chunks(users, chunk_size):
            tasks = (count(user) for user in chunk)
            await gather(*tasks)
        logger.debug("[STORAGE] Database updated")
    except Exception as e:
        logger.log_traceback(error=e)
