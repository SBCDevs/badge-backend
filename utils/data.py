from itertools import islice

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
