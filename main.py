from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv; load_dotenv()
from asyncio import get_running_loop, gather
from fastapi import FastAPI, Request
from roblox import Client, BaseGroup
from dateutil.parser import parse
from aiohttp import ClientSession
from json import load, dump
from logger import Logger
from uvicorn import run
from os import getenv

app = FastAPI()
logger = Logger()
client = Client(token=getenv("cookie"))

def format_day(iso_timestamp: str):
    day_endings = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}
    day = int(parse(iso_timestamp).strftime("%d"))
    return f"{day}{day_endings.get(day, 'th')}"

def date_format(iso_timestamp: str):
    return parse(iso_timestamp).strftime(f'%A, {format_day(iso_timestamp)} %B %Y')

def save_db(db_file="db.json"):
    with open(db_file, "w") as f: dump(db, f, indent=4)

try:
    with open("db.json","r") as f: db: dict = load(f)
except Exception as e: 
    logger.log_traceback(error=e)
    db = {"users": {}, "blacklisted": []}
    save_db()

async def update_ranking(user: str, place: int, count: int):
    # 25k : 32424261, # Skilled
    # 50k : 33901017, # Expert
    # 75k : 47370121, # Master
    # 100k : 33901028, # Legend
    # Top 10 : 67852183 # Badge Champions
    
    try:
        group_id = 4851486
        group = await client.get_group(group_id)
        u = await client.get_user(int(user))
        for role in await u.get_group_roles():
            if role.group.id == group_id:
                user_role = role.id
                break
        else:
            logger.info(f"[RANKING] {u.name} is not in SBC")
            return
        if user_role not in [32424203, 32424261, 33901017, 47370121, 33901028, 67852183]: return
        role = None
        if   (count >= 100_000): role = 33901028
        elif (count >=  75_000): role = 47370121
        elif (count >=  50_000): role = 33901017
        elif (count >=  25_000): role = 32424261
        else: role = 32424203
        if   (place <=     10): role = 67852183
        if user_role != role:
            logger.info(f"[RANKING] Promoting {u.name} to {role}")
            await group.set_role(int(user), role)
    except Exception as e:
        logger.log_traceback(error=e)

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
            get_running_loop().create_task(update_ranking(userid, place, db["users"][userid].get("count", 0)))
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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index_HTML():
    return "<html><head><title>Badge Tracker</title></head><body><h1>Online!</h1></body></html>"

@app.get("/api/progress/{user}")
async def api_count_progress(user: int):
    user = str(user)
    try: db["users"][user]
    except KeyError: return {"success": False, "message": "User not found"}
    return {"success": True, "data": {
        "quick_counting": db["users"][user].get("quick_counting", False),
        "counting": db["users"][user].get("counting", False),
        "count": db["users"][user].get("count", 0)
    }}

@app.get("/api/rank/{user}")
async def api_leaderboard_rank(user: int):
    try:
        await reorder_leaderboard()
        user = str(user)
        return {"success": True, "rank": db["users"][user]["place"]}
    except KeyError: return {"success": False, "message": "User not found"}

@app.get("/api/qc/{user}/{key}")
@app.post("/api/qc/{user}/{key}")
async def api_badge_quickcount(user: int, key: str):
    user = str(user)
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    if user in db.get("blacklisted", []):
        return {"success": False, "message": "User is blacklisted"}
    if db.get("users", {}).get(user) and (db["users"][user]["counting"] or db["users"][user]["quick_counting"]):
        return {"success": False, "message": "User is already being counted"}
    get_running_loop().create_task(quickcount(user))
    return {"success": True, "message": "Started counting"}

@app.get("/api/count/{user}/{key}")
@app.post("/api/count/{user}/{key}")
async def api_badge_count(user: int, key: str):
    user = str(user)
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    if user in db.get("blacklisted", []):
        return {"success": False, "message": "User is blacklisted"}
    if db.get("users", {}).get(user) and (db["users"][user]["counting"] or db["users"][user]["quick_counting"]):
        return {"success": False, "message": "User is already being counted"}
    get_running_loop().create_task(count(user))
    return {"success": True, "message": "Started counting"}

@app.get("/api/blacklist/{user}/{key}")
@app.post("/api/blacklist/{user}/{key}")
async def api_count_blacklist(user: int, key: str):
    user = str(user)
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    if user in db.get("blacklisted", []):
        return {"success": False, "message": "User already blacklisted"}
    if db.get("users", {}).get(user):
        del db["users"][user]
    db["blacklisted"].append(user)
    save_db()
    await reorder_leaderboard()
    return {"success": True, "message": "User blacklisted"}

@app.get("/api/unblacklist/{user}/{key}")
@app.delete("/api/unblacklist/{user}/{key}")
async def api_count_unblacklist(user: int, key: str):
    user = str(user)
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    if user not in db.get("blacklisted", []):
        return {"success": False, "message": "User not blacklisted"}
    db["blacklisted"].remove(user)
    save_db()
    await reorder_leaderboard()
    return {"success": True, "message": "User unblacklisted"}

@app.get("/api/clearbadges/{user}/{key}")
@app.delete("/api/clearbadges/{user}/{key}")
async def api_clear_badges(user: int, key: str):
    user = str(user)
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    if not db.get("users", {}).get(user): return {"success": False, "message": "User not found"}
    try: del db["users"][user]["count"]
    except KeyError: pass
    try: del db["users"][user]["cursor_count"]
    except KeyError: pass
    try: del db["users"][user]["cursor"]
    except KeyError: pass
    db["users"][user]["counting"] = False
    save_db()
    await reorder_leaderboard()
    return {"success": True, "message": f"Badges cleared for {user}"}

@app.get("/api/cleardb/{key}")
@app.delete("/api/cleardb/{key}")
async def api_clear_database(key: str):
    if key != getenv("apikey"): return {"success": False, "message": "Invalid API key"}
    save_db(db_file="db.backup.json")
    users = list(db["users"].keys())
    db["users"] = {}
    save_db()
    tasks = (count(user) for user in users)
    get_running_loop().create_task(gather(*tasks))
    get_running_loop().create_task(update_db())
    return {"success": True, "message": "Successfully reset the whole database and started recounting everyone."}

@app.get("/api/leaderboard")
async def api_badge_leaderboard():
    return {"success": True, "data": await reorder_leaderboard()}

@app.get("/api/first/{user}")
async def api_first_badge(user: int):
    user = str(user)
    async with ClientSession() as session:
        try:
            async with session.get(f"https://badges.roblox.com/v1/users/{user}/badges?limit=10&sortOrder=Asc") as resp: response = await resp.json()
            d = {
                i: (date_format(response["data"][0][i]) if i in ("created", "updated") else response["data"][0][i])
                for i in response["data"][0]
            }
            async with session.get(f'https://badges.roblox.com/v1/users/{user}/badges/awarded-dates?badgeIds={d["id"]}') as resp: response = await resp.json()
            d["awardedDate"] = date_format(response["data"][0]["awardedDate"])
        except Exception as e:
            logger.log_traceback(error=e)
            return {"success": False, "message": "Error whilst fetching badge data"}
    return {"success": True, "data": d}

@app.get("/api/last/{user}")
async def api_last_badge(user: int):
    user = str(user)
    async with ClientSession() as session:
        try:
            async with session.get(f"https://badges.roblox.com/v1/users/{user}/badges?limit=10&sortOrder=Desc") as resp: response = await resp.json()
            d = {
                i: (date_format(response["data"][0][i]) if i in ("created", "updated") else response["data"][0][i])
                for i in response["data"][0]
            }
            async with session.get(f'https://badges.roblox.com/v1/users/{user}/badges/awarded-dates?badgeIds={d["id"]}') as resp: response = await resp.json()
            d["awardedDate"] = date_format(response["data"][0]["awardedDate"])
        except Exception as e:
            logger.log_traceback(error=e)
            return {"success": False, "message": "Error whilst fetching badge data"}
    return {"success": True, "data": d}

@app.get("/api/stats")
async def api_stats():
    return {"success": True, "data": {
        "users": len(db.get("users", {})),
        "counting": len([i for i in db.get("users", {}) if (db["users"][i].get("counting", False) or db["users"][i].get("quick_counting", False))]),
        "badges": sum(db['users'][i].get("count", 0) for i in db.get('users', {}))
    }}

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.log_traceback(error=exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    )

@app.on_event("startup")
async def on_startup():
    for user in db["users"]:
        db["users"][user]["counting"] = False
        db["users"][user]["quick_counting"] = False
    get_running_loop().create_task(reorder_leaderboard())
    get_running_loop().create_task(update_db())
    # async with ClientSession() as session:
        # async with session.post("https://catalog.roblox.com/", cookies=cookies) as res:
            # logger.info(f"[{res.status}] catalog.roblox.com")
            # logger.info(res.headers)
            # headers['X-CSRF-TOKEN'] = res.headers['X-CSRF-TOKEN']

async def update_db():
    logger.info("Updating database...")
    for i in range(0, len(db["users"]), 150):
        logger.info(f"Updating chunk {i}/{len(db['users'])}")
        tasks = (count(user) for user in db["users"][i:i + 150])
        await gather(*tasks)
        logger.info(f"Chunk {i}/{len(db['users'])} updated")
    logger.info("Database updated")

@app.on_event("shutdown")
async def on_shutdown():
    save_db()
    
if __name__ == "__main__": run(app, port=8684)
