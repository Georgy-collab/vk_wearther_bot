import json
import os
from datetime import datetime


def save_to_file(data: dict) -> None:
    with open("weather.json", "w", encoding="UTF-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def file_hour_3_update() -> bool:

    file_path = "weather.json"
    file_exists = os.path.exists(file_path)

    if file_exists:
        file_time = os.path.getmtime(file_path)
        now = datetime.now().timestamp()
        hours_since_update = (now - file_time) / 3600
        if hours_since_update <= 3:
            return True
        else:
            return False
    return False


def read_from_file() -> dict | None:
    if file_hour_3_update():
        with open("weather.json", "r", encoding="UTF-8") as file:
            return json.load(file)
    else:
        return None