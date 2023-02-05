from surrealdb.clients.http import HTTPClient
from .types import User
from os import getenv
from typing import Any, Union
import dataclasses

client = HTTPClient(
    f"http://{getenv('DB_HOST')}:{getenv('DB_PORT')}",
    namespace=getenv("DB_NAMESPACE"),
    database=getenv("DB_DATABASE"),
    username=getenv("DB_USER"),
    password=getenv("DB_PASS")
)

def _parse_user_id(user_id: Any) -> str:
    return str(user_id)

async def get_user(user_id: str) -> User:
    user_id = _parse_user_id(user_id)
    return User(await client.select_one("users", user_id))

async def update_user(user_id: str, partial_data: Union[dict, User]):
    user_id = _parse_user_id(user_id)
    if isinstance(partial_data, User):
        partial_data = dataclasses.asdict(partial_data)

    await client.upsert_one("users", user_id, partial_data)

async def set_user(user_id: str, data: Union[dict, User]):
    user_id = _parse_user_id(user_id)
    if isinstance(data, User):
        data = dataclasses.asdict(data)

    await client.replace_one("users", user_id, data)

async def create_user(user_id: str, data: Union[dict, User]):
    user_id = _parse_user_id(user_id)
    if isinstance(data, User):
        data = dataclasses.asdict(data)

    await client.create_one("users", user_id, data)

async def delete_user(user_id: str):
    user_id = _parse_user_id(user_id)
    await client.delete_one("users", user_id)
