import os
import uuid
from pathlib import Path

from .store import FSStore
from .store.progress import Progress

# 常量
PORT = 9000
COMFY_UI_PORT = 8188
COMFY_UI_ROOT = "/root/comfyui"
WATCHDOG_INTERVAL_MS = 500
LISTEN = False
LISTEN_HOST = "0.0.0.0"
START_HOST = "0.0.0.0"

# STORE 常量
TASK_DIR = "/mnt/auto/comfyui/tasks"

# 变量
CLIENT_ID = str(uuid.uuid4())

def create_task_store():
    fs_store = FSStore(TASK_DIR)
    return Progress(fs_store)

TASK_STORE = create_task_store()

def is_debug():
    debug_env = os.getenv("DEBUG", "").lower()
    return debug_env not in ["0", "false", ""]

DEBUG = is_debug()

if LISTEN:
    COMFY_UI_HOST = f"{LISTEN_HOST}:{COMFY_UI_PORT}"
else:
    COMFY_UI_HOST = f"127.0.0.1:{COMFY_UI_PORT}"