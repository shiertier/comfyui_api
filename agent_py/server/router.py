from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from ..config import COMFY_UI_HOST
from .progress import progress
from .proxy import proxy
from .run import run_comfyui_http, run_comfyui_websocket

def set_cors(request: BaseHTTPRequestHandler):
    request.send_header('Access-Control-Allow-Origin', request.headers.get('Origin'))
    request.send_header('Access-Control-Allow-Headers', '*')
    request.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE')
    request.send_header('Access-Control-Allow-Credentials', 'true')
    if request.command == 'OPTIONS':
        request.send_response(200)
        request.end_headers()
        return True
    return False

def router(request: BaseHTTPRequestHandler):
    # Determine the path and dispatch to the appropriate handler
    if request.path == "/api/run":
        set_cors(request)
        run_comfyui_http(request)
    elif request.path == "/api/run/ws":
        # WebSocket handling is typically done differently in Python
        # Uncomment if CORS is needed for WebSockets
        # set_cors(request)
        run_comfyui_websocket(request)
    elif request.path == "/api/status":
        set_cors(request)
        progress(request)
    elif request.path.startswith("/comfyui"):
        proxy(request)
    else:
        request.send_error(404, "Not Found")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        router(self)

    def do_POST(self):
        router(self)

    def do_OPTIONS(self):
        set_cors(self)