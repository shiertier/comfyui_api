import base64
import json
import random
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests
import time

from websocket import WebSocketApp
from config import CLIENT_ID, TASK_STORE, COMFY_UI_HOST
from log import debugf, errorf

from ..comfyui.api import prompt, progress, upload_image
from ..store.progress import TProgress, TProgressNode, TProgressNodeImage

def read_url_bytes(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def read_base64_bytes(b64: str) -> bytes:
    return base64.b64decode(b64.strip())

def parse_prompt(prompt: dict):
    for key, value in prompt.items():
        if value["class_type"] == "LoadImage":
            image = value["inputs"].get("image")
            if not image:
                continue

            image_bytes = None
            if image.startswith("http://") or image.startswith("https://"):
                image_bytes = read_url_bytes(image)
            elif len(image) >= 64:
                image_bytes = read_base64_bytes(image)

            if image_bytes:
                file = upload_image(image_bytes, False)
                value["inputs"]["image"] = file["name"]
                prompt[key] = value

def run_comfyui_task(client_id: str, task_id: str, prompt: dict, callback: callable) -> TProgress:
    parse_prompt(prompt)

    prompt_id = prompt(client_id, prompt)
    log_prefix = f"[client {client_id}] [task {task_id}] [prompt {prompt_id}]"
    debugf(f"{log_prefix} start to get progress")

    progress = TProgress()
    for node_id in prompt.keys():
        progress[node_id] = TProgressNode()

    def handle_message(msg: dict) -> bool:
        debugf(f"{log_prefix} receive message {msg}")
        if not msg:
            errorf(f"{log_prefix} websocket msg is nil, ignore it")
            return False

        if msg["data"]["prompt_id"] != prompt_id:
            return False

        callback(progress)

        now = int(time.time())
        node_id = msg["data"]["node"]
        current_node_progress = progress.get(node_id, TProgressNode())
        current_node_progress.last_updated = now

        if msg["type"] in ["execution_start", "executing"] and node_id == "":
            debugf(f"{log_prefix} prompt finished")
            return True
        elif msg["type"] in ["execution_start", "executing"]:
            debugf(f"{log_prefix} node {node_id} start")
            current_node_progress.start = now
            if current_node_progress.max == 0:
                current_node_progress.max = 1
        elif msg["type"] in ["execution_error", "executed"]:
            debugf(f"{log_prefix} node {node_id} finished")
            if current_node_progress.max == 0 and current_node_progress.value == 0:
                current_node_progress.max = 1
                current_node_progress.value = 1

            if prompt[node_id]["class_type"] == "SaveImage" and msg["data"]["output"]["images"]:
                current_node_progress.images = [
                    TProgressNodeImage(
                        filename=img["filename"],
                        subfolder=img["subfolder"],
                        type=img["type"]
                    ) for img in msg["data"]["output"]["images"]
                ]

        elif msg["type"] == "progress":
            debugf(f"{log_prefix} node {node_id} progress {msg['data']['value']}/{msg['data']['max']} {msg['data']['value']*100//msg['data']['max']}%")
            current_node_progress.max = msg["data"]["max"]
            current_node_progress.value = msg["data"]["value"]

        progress[node_id] = current_node_progress
        return False

    progress(client_id, handle_message)
    return progress

def run_comfyui_http(request: BaseHTTPRequestHandler):
    task_id = request.headers.get("task-id", str(uuid.uuid4()))
    prompt = json.loads(request.rfile.read(int(request.headers.get("Content-Length"))))

    def callback(progress: TProgress):
        TASK_STORE.save_progress(task_id, progress)

    try:
        progress = run_comfyui_task(CLIENT_ID, task_id, prompt, callback)
        request.send_response(200)
        request.send_header('Content-type', 'application/json')
        request.end_headers()
        request.wfile.write(json.dumps(progress).encode())
    except Exception as e:
        errorf(f"run comfyui error: {e}")
        request.send_error(500, str(e))

def run_comfyui_websocket(request: BaseHTTPRequestHandler):
    task_id = request.headers.get("task-id", str(uuid.uuid4()))
    ws = WebSocketApp(f"ws://{urlparse(request.path).netloc}/ws?clientId={task_id}",
                      on_message=lambda ws, msg: on_message(ws, msg, task_id),
                      on_error=lambda ws, err: on_error(ws, err),
                      on_close=lambda ws: on_close(ws))
    ws.run_forever()

def on_message(ws, message, task_id):
    prompt = json.loads(message)

    def callback(progress: TProgress):
        ws.send(json.dumps({"type": "progress", "data": progress}))

    try:
        progress = run_comfyui_task(CLIENT_ID, task_id, prompt, callback)
        for node_id, node_progress in progress.items():
            if node_progress.images:
                images = []
                for img in node_progress.images:
                    response = requests.get(f"http://{COMFY_UI_HOST}/view?filename={img.filename}&type={img.type}&subfolder={img.subfolder}&rand={random.random()}")
                    response.raise_for_status()
                    images.append(base64.b64encode(response.content).decode())
                node_progress.results = images
                progress[node_id] = node_progress

        ws.send(json.dumps({"type": "result", "data": progress}))
    except Exception as e:
        ws.send(json.dumps({"type": "error", "data": str(e)}))

def on_error(ws, error):
    errorf(f"websocket error: {error}")

def on_close(ws):
    debugf("websocket closed")

def router(request: BaseHTTPRequestHandler):
    if request.path == "/api/run":
        run_comfyui_http(request)
    elif request.path == "/api/run/ws":
        run_comfyui_websocket(request)
    else:
        request.send_error(404, "Not Found")