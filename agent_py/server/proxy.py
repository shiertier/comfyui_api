from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
from ..config import COMFY_UI_HOST

class ReverseProxy:
    def __init__(self, target_url):
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)

    def __call__(self, environ, start_response):
        environ['wsgi.url_scheme'] = self.parsed_url.scheme
        environ['HTTP_HOST'] = self.parsed_url.netloc
        environ['PATH_INFO'] = environ['PATH_INFO']
        environ['QUERY_STRING'] = environ['QUERY_STRING']
        environ['SCRIPT_NAME'] = ''

        return SharedDataMiddleware(None, {})(environ, start_response)

comfyui_proxy = ReverseProxy(f"http://{COMFY_UI_HOST}")

def proxy(request: BaseHTTPRequestHandler):
    @Request.application
    def application(req):
        response = Response.from_app(comfyui_proxy, req.environ)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    application(Request(request.environ))

def router(request: BaseHTTPRequestHandler):
    if request.path.startswith("/comfyui"):
        proxy(request)
    else:
        request.send_error(404, "Not Found")