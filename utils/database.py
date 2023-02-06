from surrealdb.clients.http import HTTPClient
from surrealdb.common.exceptions import SurrealException
from ..models.user import User
from typing import Any, Union, Dict
from os import getenv
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
    try: user = await client.select_one("users", user_id)
    except SurrealException: user = {} # Empty user (Default)
    return User(user)

async def update_user(user_id: str, partial_data: Union[Dict[str, Any], User]):
    user_id = _parse_user_id(user_id)
    if isinstance(partial_data, User):
        partial_data = dataclasses.asdict(partial_data)
    
    # Lookup the user
    user = dataclasses.asdict(await get_user(user_id))
    
    # Merge the user with the partial data
    user.update(partial_data)

    await set_user(user_id, user)

async def set_user(user_id: str, data: User):
    user_id = _parse_user_id(user_id)
    data = dataclasses.asdict(data)
    await client.replace_one("users", user_id, data)

async def delete_user(user_id: str):
    user_id = _parse_user_id(user_id)
    await client.delete_one("users", user_id)
