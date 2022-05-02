from .data import db, save_db, chunks
__import__("dotenv").load_dotenv()
from aiohttp import ClientSession
from asyncio import gather
from os import getenv
from .log import logger

chunk_size = int(getenv("chunk_size", default=250))

async def reorder_leaderboard():
    try:
        users = dict(
            sorted({
                    i: dict(db["users"][i]).get("count", 0)
                    for i in db.get("users", [])
                }.items(),
                key = lambda x:x[1],
                reverse = True
        ))
        lb = []
        for place, userid in enumerate(users, start=1):
            lb.append({
                "place": place,
                "count": db["users"][userid].get("count", 0),
                "userId": int(userid),
                "quick_counting": db["users"][userid].get("quick_counting", False),
                "counting": db["users"][userid].get("counting", False),
            })
            db["users"][userid]["place"] = place
        save_db()
        return lb
    except Exception as e:
        logger.log_traceback(error=e)

async def quickcount(user: str):
    try:
        if not db.get("users"): db["users"] = {}
        if not db["users"].get(user):
            db["users"][user] = {
                "count": 0,
                "quick_counting": False,
                "counting": False,
                "place": 0,
                "cursor_count": 0,
                "cursor": None
            }
        if db["users"][user].get("counting", False) or db["users"][user].get("quick_counting", False): return
        if not db["users"][user].get("count"):
            db["users"][user]["count"] = 0
        db["users"][user]["quick_counting"] = True
        logger.debug(f"[QUICK COUNT] {db['users'][user]}")

        params = {"limit": 100, "sortOrder": "Asc"}
        request_url = f"https://badges.roblox.com/v1/users/{user}/badges"

        if db["users"][user].get("cursor"):
            params["cursor"] = db["users"][user]["cursor"]
            db["users"][user]["count"] = db["users"][user].get("cursor_count", 0)

        async with ClientSession() as session:
            while True:
                async with session.get(request_url, params=params) as resp:
                    response: dict = await resp.json()
                    db["users"][user]["cursor_count"] = db["users"][user].get("count", 0)
                    db["users"][user]["count"] += len(response.get("data", []))
                    cursor = response.get("nextPageCursor")
                    logger.debug(f"[QUICK COUNT] [{user}] {len(response.get('data', []))} Cursor: {cursor}")
                if cursor:
                    params["cursor"] = cursor
                    db["users"][user]["cursor"] = cursor
                else:
                    db["users"][user]["quick_counting"] = False
                    db["users"][user]["counting"] = False
                    break
        save_db()
        await reorder_leaderboard()
    except Exception as e:
        logger.log_traceback(error=e)

async def count(user: str):
    try:
        if not db.get("users"): db["users"] = {}
        if not db["users"].get(user):
            db["users"][user] = {
                "count": 0,
                "quick_counting": False,
                "counting": False,
                "place": 0,
                "cursor_count": 0,
                "cursor": None
            }
        if db["users"][user].get("counting", False) or db["users"][user].get("quick_counting", False): return
        db["users"][user]["counting"] = True
        logger.debug(f"[SLOW COUNT] {db['users'][user]}")

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
                    logger.debug(f"[SLOW COUNT] [{user}] {len(response.get('data', []))} Cursor: {cursor}")
                if current_cursor:
                    cursor = current_cursor
                    params["cursor"] = current_cursor
                else:
                    db["users"][user]["quick_counting"] = False
                    db["users"][user]["counting"] = False
                    db["users"][user]["cursor"] = cursor
                    db["users"][user]["count"] = user_badge_count
                    db["users"][user]["cursor_count"] = cursor_count
                    break
        save_db()
        await reorder_leaderboard()
    except Exception as e:
        logger.log_traceback(error=e)

async def update_db():
    try:
        logger.debug("[STORAGE] Updating database...")
        for chunk in chunks(db['users'], chunk_size):
            tasks = (count(user) for user in chunk)
            await gather(*tasks)
        logger.debug("[STORAGE] Database updated")
    except Exception as e: logger.log_traceback(error=e)
