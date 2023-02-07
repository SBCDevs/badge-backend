from roblox.utilities.exceptions import TooManyRequests, InternalServerError
from fastapi_utils.tasks import repeat_every
from fastapi.responses import JSONResponse
from utils import reorder_leaderboard
from fastapi import FastAPI, Request

__import__("dotenv").load_dotenv()
from roblox import Client
from logger import Logger
from asyncio import sleep
from uvicorn import run
from os import getenv
from pages import api
import events
import pages
from httpx import RemoteProtocolError, ReadTimeout, ConnectError

app = FastAPI(
    title="SBC Badge Counter", version="3.0.0", docs_url="/docs", redoc_url="/redoc"
)
logger = Logger()
client = Client(token=str(getenv("COOKIE")))
group_id = 4851486
chunk_size = int(getenv("chunk_size", default=250))

app.include_router(pages.router, prefix="", tags=["Pages"])

app.include_router(api.router, prefix="/api", tags=["API"])

app.include_router(events.router)


@app.on_event("startup")
@repeat_every(seconds=(60 * 60 * 24))
async def update_ranking():
    # 25k : 32424261, # Skilled
    # 50k : 33901017, # Expert
    # 75k : 47370121, # Master
    # 100k : 33901028, # Legend
    # Top 10 : 67852183 # Badge Champions

    lb = await reorder_leaderboard()
    group = await client.get_group(group_id)

    for user in lb:
        while True:
            try:
                u = await client.get_user(user.userId)
                for role in await u.get_group_roles():
                    if role.group is None:
                        continue
                    
                    if role.group.id == group_id:
                        user_role = role.id
                        break
                else:
                    logger.debug(f"[RANKING] {u.name} is not in SBC")
                    continue
                
                if user_role not in [
                    32424203,
                    32424261,
                    33901017,
                    47370121,
                    33901028,
                    67852183,
                ]: continue
                
                role = None
                if user.count >= 100_000:
                    role = 33901028
                elif user.count >= 75_000:
                    role = 47370121
                elif user.count >= 50_000:
                    role = 33901017
                elif user.count >= 25_000:
                    role = 32424261
                else:
                    role = 32424203
                if user.place <= 10:
                    role = 67852183
                if user_role != role:
                    logger.debug(f"[RANKING] Promoting {u.name} to {role}")
                    await group.set_role(user.userId, role)
                else:
                    logger.debug(f"[RANKING] {u.name} already has {role}")
                break
            except TooManyRequests:
                logger.warn(
                    "[RANKING] Too many requests, sleeping for 10 seconds and retrying... (Consider using smaller chunks!)"
                )
                await sleep(10)
            except InternalServerError:
                logger.error(
                    "[RANKING] Internal server error, sleeping for 2 and a half seconds and retrying..."
                )
                await sleep(2.5)
            except (RemoteProtocolError, ReadTimeout, ConnectError):
                logger.warn(
                    "[RANKING] Connection error, sleeping for 10 seconds and retrying..."
                )
                await sleep(10)
            except Exception as e:
                logger.log_traceback(error=e)
                break


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.log_traceback(error=exc)
    return JSONResponse(
        status_code=500, content={"success": False, "message": "Internal server error"}
    )


if __name__ == "__main__":
    run(app, port=8684)
