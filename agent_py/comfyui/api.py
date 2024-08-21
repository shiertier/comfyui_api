import json
import uuid
import requests
import websocket
from io import BytesIO
from uuid import uuid4
from ..log import debugf, errorf
from ..config import COMFY_UI_HOST

def prompt(client_id: str, prompt: dict) -> str:
    url = f"http://{COMFY_UI_HOST}/prompt"
    payload = {
        "client_id": client_id,
        "prompt": prompt
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Prompt request failed: {response.text}")
    result = response.json()
    return result["prompt_id"]

def progress(client_id: str, callback: callable) -> None:
    url = f"ws://{COMFY_UI_HOST}/ws?clientId={client_id}"
    ws = websocket.WebSocketApp(url,
                                on_message=lambda ws, msg: on_message(ws, msg, callback),
                                on_error=lambda ws, err: on_error(ws, err),
                                on_close=lambda ws: on_close(ws))
    ws.run_forever()

def on_message(ws, message, callback):
    debugf(f"got message from client, {message}")
    msg = json.loads(message)
    if callback(msg):
        ws.close()

def on_error(ws, error):
    errorf(f"websocket error: {error}")

def on_close(ws):
    debugf("websocket closed")

def upload_image(image: bytes, overwrite: bool) -> dict:
    url = f"http://{COMFY_UI_HOST}/upload/image"
    filename = str(uuid4())
    files = {
        "image": (filename, image, "image/png"),
        "overwrite": ("overwrite", "1" if overwrite else "0")
    }
    response = requests.post(url, files=files)
    if response.status_code != 200:
        raise Exception(f"Upload image failed: {response.text}")
    result = response.json()
    return result