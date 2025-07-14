import json
import os

DATA_FILE = "resources/tasks.json"
POS_FILE = "resources/window_pos.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

def save_window_pos(x, y):
    with open(POS_FILE, "w", encoding="utf-8") as f:
        json.dump({"x": x, "y": y}, f)

def load_window_pos():
    if os.path.exists(POS_FILE):
        with open(POS_FILE, "r", encoding="utf-8") as f:
            pos = json.load(f)
            return pos.get("x", 0), pos.get("y", 50)
    return 0, 50