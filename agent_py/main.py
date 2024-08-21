import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from .config import PORT, COMFY_UI_PORT
from .utils.log import errorf
from .utils.watchdog import new_watchdog
from .server import router

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        router(self)

    def do_POST(self):
        router(self)

    def do_PUT(self):
        router(self)

    def do_DELETE(self):
        router(self)

def main():
    # 先拉起 ComfyUI
    wd = new_watchdog(COMFY_UI_PORT, sys.argv[1:])
    err = wd.start()
    if err is not None:
        errorf(f"start comfyui failed, due to {err}", f"启动 ComfyUI 失败，因为 {err}")
        return

    # 再监听当前 agent 的端口
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()