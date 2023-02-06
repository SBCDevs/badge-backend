from surrealdb.clients.http import HTTPClient
from dotenv import load_dotenv; load_dotenv()
from typing import Dict, List, Any
from models.user import User
from os import getenv
import dataclasses
import argparse
import asyncio
import json

USERS_TABLE = "users"

parser = argparse.ArgumentParser(
    prog="Database Migrator",
    description="Used to migrate the database from a old .json file to the new SurrealDB database"
)
parser.add_argument("--clear-users", action='store_true')
args = parser.parse_args()

client = HTTPClient(
    f"http://{getenv('DB_HOST')}:{getenv('DB_PORT')}",
    namespace=str(getenv("DB_NAMESPACE")),
    database=str(getenv("DB_DATABASE")),
    username=str(getenv("DB_USER")),
    password=str(getenv("DB_PASS"))
)

db_file = input("Database file: ")

with open(db_file) as f:
    db = json.load(f)

users: Dict[str, Dict[str, Any]] = db["users"]
blacklisted: List[int] = db["blacklisted"]

new_db: Dict[str, User] = {}

async def main():
    print()
    if (args.clear_users):
        await client.delete_all("users")
        print("Users cleared!")
    
    for index, i in enumerate(users.items()):
        perc = round(index, len(db_file) * 100)
        print(f"Parsing users.. {perc}%", end="\r")
        key, value = i
        new_db[key] = User(**value)
    print("Parsing users.. DONE")

    for index, i in enumerate(users):
        perc = round(index, len(db_file) * 100)
        print(f"Parsing blacklist.. {perc}%", end="\r")
        user = new_db[i]
        user.blacklisted = True
        new_db[i] = user
    print("Parsing blacklist.. DONE")

    for index, i in enumerate(new_db.items()):
        perc = round(index, len(db_file) * 100)
        print(f"Writing to database.. {perc}%", end="\r")
        user_id, user = i
        await client.create_one(USERS_TABLE, user_id, dataclasses.asdict(user))

    print("Writing to database.. DONE")

asyncio.get_event_loop().run_until_complete(main())
