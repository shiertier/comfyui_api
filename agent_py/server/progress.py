from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from ..config import TASK_STORE
from ..log import errorf

class HTTPError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message

    def __str__(self):
        return f"HTTP Error {self.status}: {self.message}"

def error_wrapper(status: int, err: Exception) -> HTTPError:
    return HTTPError(status, str(err))

def progress(request: BaseHTTPRequestHandler):
    query = parse_qs(urlparse(request.path).query)
    id = query.get("id", [None])[0]
    if id is None:
        request.send_error(400, "Missing id parameter")
        return

    try:
        progress = TASK_STORE.load_progress(id)
    except Exception as e:
        errorf(f"query progress got failed: {e}")
        request.send_error(404, str(error_wrapper(404, e)))
        return

    request.send_response(200)
    request.send_header('Content-type', 'application/json')
    request.end_headers()
    request.wfile.write(progress.to_json().encode())

def router(request: BaseHTTPRequestHandler):
    if request.path.startswith("/progress"):
        progress(request)
    else:
        request.send_error(404, "Not Found")