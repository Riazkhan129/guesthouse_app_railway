# db_config.py

import json

DB_PATH_FILE = "db_path.txt"

def save_db_path(path):
    with open(DB_PATH_FILE, "w") as f:
        json.dump({"db_path": path}, f)

def load_db_path():
    with open(DB_PATH_FILE, "r") as f:
        data = json.load(f)
        return data["db_path"]  # ✅ Properly get the "db_path" value
