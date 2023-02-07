from .async_util import semaphore_wrapper
__import__("dotenv").load_dotenv()
from aiohttp import ClientSession
from . import database as db
from asyncio import gather
from typing import List
from .log import logger
from os import getenv
import asyncio
from .. import models

CHUNK_SIZE = int(getenv("CHUNK_SIZE", default=250))

async def reorder_leaderboard() -> List[models.LeaderboardEntry]:
    try:
        users = dict(
            sorted(
                { i._id: i.count for i in await db.get_all_users() }.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )
        lb = []
        for place, userid in enumerate(users, start=1):
            user_id = str(userid)
            user = await db.get_user(user_id)
            lb.append(models.LeaderboardEntry(
                place=place,
                count=user.count,
                userId=userid,
                quick_counting=user.quick_counting,
                counting=user.counting
            ))
            await db.update_user(user_id, {
                "place": place
            })
        return lb
    except Exception as e:
        logger.log_traceback(error=e)
        return []


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
    try:
        logger.debug("[STORAGE] Updating database...")
        users = await db.get_all_users()
        
        semaphore = asyncio.Semaphore(CHUNK_SIZE)
        
        tasks = [
            asyncio.create_task(
                semaphore_wrapper(
                    count(str(user._id)),
                    semaphore
                )
            ) for user in users
        ]
        
        await gather(*tasks)
        logger.debug("[STORAGE] Database updated")
    except Exception as e:
        logger.log_traceback(error=e)


async def update_users(users: List[models.User]):
    try:
        logger.debug(f"[STORAGE] Updating database with {len(users)}...")
        semaphore = asyncio.Semaphore(CHUNK_SIZE)
        
        tasks = [
            asyncio.create_task(
                semaphore_wrapper(
                    count(str(user._id)),
                    semaphore
                )
            ) for user in users
        ]
        
        await gather(*tasks)
        logger.debug("[STORAGE] Database updated")
    except Exception as e:
        logger.log_traceback(error=e)
