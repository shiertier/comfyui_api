import json
import requests
from typing import Any, Dict
from log import debugf

class HTTPError(Exception):
    """HTTP Error with status code and body"""

    def __init__(self, status: int, body: str):
        super().__init__(f"http error, status: {status}, body: {body}")
        self.status = status
        self.body = body

def read_to_json(response: requests.Response, target: Any) -> None:
    """Read binary content from response into JSON object"""
    if target is None:
        return

    try:
        data = response.json()
        if isinstance(target, dict):
            target.update(data)
        else:
            target.update(data)  # Assuming target is a dict-like object
    except json.JSONDecodeError as e:
        raise e

def http_get(url: str, target: Any) -> requests.Response:
    """Perform an HTTP GET request and deserialize response to JSON"""

    response = requests.get(url)
    if response.status_code != 200:
        body = response.text
        raise HTTPError(status=response.status_code, body=body)
    
    read_to_json(response, target)
    return response


def http_post(url: str, body: Dict[str, Any], target: Any) -> requests.Response:
    """Perform an HTTP POST request with JSON body and deserialize response to JSON"""
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=body, headers=headers)

    debugf("Request body: %s", json.dumps(body))

    if response.status_code != 200:
        body = response.text
        raise HTTPError(status=response.status_code, body=body)

    read_to_json(response, target)
    return response
