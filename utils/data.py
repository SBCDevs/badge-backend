from itertools import islice
from json import load, dump
from datetime import datetime


def toBoolean(string: str):
    if not string:
        return None
    if string.lower() in {"true", "yes", "1"}:
        return True
    elif string.lower() in {"false", "no", "0"}:
        return False
    return None


def chunks(data: dict, size: int):
    data = data.copy()
    it = iter(data)
    for _ in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}


def list_chunks(data: list, size: int):
    for i in range(0, len(data), size):
        yield data[i : i + size]


def save_db(db_file="db.json"):
    with open(db_file, "w") as f:
        dump(db, f, indent=4)


def backup_db(db_file="db.json"):
    with open(db_file, "r") as f:
        db = load(f)
    with open(f"./backups/{datetime.now().strftime('%d-%m-%Y')}.json", "w") as f:
        dump(db, f, indent=4)


try:
    with open("db.json", "r") as f:
        db: dict = load(f)
except OSError:
    db = {"users": {}, "blacklisted": []}
    save_db(db_file="db.json")
