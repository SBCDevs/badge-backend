from .exceptions import *

def toBoolean(string: str):
    if not string: return None
    if string.lower() in {'true', 'yes', '1'}: return True
    elif string.lower() in {'false', 'no', '0'}: return False
    return None
