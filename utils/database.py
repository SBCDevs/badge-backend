from surrealdb.clients.http import HTTPClient
from surrealdb.common.exceptions import SurrealException
from ..models.user import User
from typing import Any, Union, Dict
from os import getenv
import dataclasses

client = HTTPClient(
    f"http://{getenv('DB_HOST')}:{getenv('DB_PORT')}",
    namespace=str(getenv("DB_NAMESPACE")),
    database=str(getenv("DB_DATABASE")),
    username=str(getenv("DB_USER")),
    password=str(getenv("DB_PASS"))
)

USERS_TABLE = "users"

def _parse_user_id(user_id: Any) -> str:
    return str(user_id)

async def get_user(user_id: str) -> User:
    user_id = _parse_user_id(user_id)
    try: user = await client.select_one(USERS_TABLE, user_id)
    except SurrealException: user = {} # Empty user (Default)
    return User(_id=int(user_id), **user)

async def update_user(user_id: str, partial_data: Union[Dict[str, Any], User]):
    user_id = _parse_user_id(user_id)
    if isinstance(partial_data, User):
        partial_data = dataclasses.asdict(partial_data)
    
    # Lookup the user
    user = dataclasses.asdict(await get_user(user_id))
    
    # Merge the user with the partial data
    user.update(partial_data)

    await set_user(user_id, User(_id=int(user_id), **user))

async def set_user(user_id: str, data: User):
    user_id = _parse_user_id(user_id)
    set_data = dataclasses.asdict(data)
    await client.replace_one(USERS_TABLE, user_id, set_data)

async def delete_user(user_id: str):
    user_id = _parse_user_id(user_id)
    await client.delete_one(USERS_TABLE, user_id)
