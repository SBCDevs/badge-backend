from dateutil.parser import parse


def format_day(iso_timestamp: str):
    day_endings = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}
    day = int(parse(iso_timestamp).strftime("%d"))
    return f"{day}{day_endings.get(day, 'th')}"


def format_date(iso_timestamp: str):
    return parse(iso_timestamp).strftime(f"%A, {format_day(iso_timestamp)} %B %Y")
