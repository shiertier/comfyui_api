from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from ..config import COMFY_UI_HOST

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

def run_comfyui(request: BaseHTTPRequestHandler):
    if set_cors(request):
        return
    # 调用 pipeline 的逻辑
    request.send_response(200)
    request.send_header('Content-type', 'text/html')
    request.end_headers()
    request.wfile.write(b'Run ComfyUI')

def run_comfyui_websocket(request: BaseHTTPRequestHandler):
    # 调用 pipeline 的逻辑
    request.send_response(200)
    request.send_header('Content-type', 'text/html')
    request.end_headers()
    request.wfile.write(b'Run ComfyUI Websocket')

def progress(request: BaseHTTPRequestHandler):
    if set_cors(request):
        return
    # 获取进度的逻辑
    request.send_response(200)
    request.send_header('Content-type', 'text/html')
    request.end_headers()
    request.wfile.write(b'Progress')

def proxy(request: BaseHTTPRequestHandler):
    # 默认转发给 comfyui 的逻辑
    request.send_response(200)
    request.send_header('Content-type', 'text/html')
    request.end_headers()
    request.wfile.write(b'Proxy to ComfyUI')

def router(request: BaseHTTPRequestHandler):
    path = urlparse(request.path).path
    if path == '/api/run':
        run_comfyui(request)
    elif path == '/api/run/ws':
        run_comfyui_websocket(request)
    elif path == '/api/status':
        progress(request)
    else:
        proxy(request)