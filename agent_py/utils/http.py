import json
import requests
from io import BytesIO
from typing import Any, Dict, Optional

from .log import debugf

class HTTPError(Exception):
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body

    def __str__(self):
        return f"http error, status: {self.status}, body: {self.body}"

def read_to_json(r: BytesIO, target: Any) -> None:
    if target is None:
        return

    b = r.read()
    try:
        #json.loads(b.decode(), object_hook=lambda d: target.__dict__.update(d))
        target.__dict__.update(json.loads(b.decode()))
    except json.JSONDecodeError as e:
        raise e

def http_request(method: str, url: str, body: Optional[Dict[str, Any]] = None, target: Optional[Any] = None) -> requests.Response:
    if body is not None:
        body_bytes = json.dumps(body).encode()
        debugf("%s", body_bytes)
        resp = requests.request(method, url, data=body_bytes, headers={"Content-Type": "application/json"})
    else:
        resp = requests.request(method, url)

    if resp.status_code != 200:
        raise HTTPError(resp.status_code, resp.text)

    read_to_json(BytesIO(resp.content), target)
    return resp

def http_get(url: str, target: Optional[Any] = None) -> requests.Response:
    return http_request("GET", url, target=target)

def http_post(url: str, body: Dict[str, Any], target: Optional[Any] = None) -> requests.Response:
    return http_request("POST", url, body=body, target=target)