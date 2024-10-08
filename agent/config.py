import os
import uuid
from store.progress import Progress
from store.fs import FS

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


# TaskStore 任务状态的存储，可以考虑存储在 OTS、RDS 等产品，这里只实现了文件系统存储
TASK_STORE = Progress(FS(TASK_DIR))

def is_debug():
    debug_env = os.getenv("DEBUG", "").lower()
    return debug_env not in ["0", "false", ""]

DEBUG = is_debug()

if LISTEN:
    COMFY_UI_HOST = f"{LISTEN_HOST}:{COMFY_UI_PORT}"
else:
    COMFY_UI_HOST = f"127.0.0.1:{COMFY_UI_PORT}"
