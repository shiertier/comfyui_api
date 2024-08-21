import json
from ..utils.http import HTTPError

class ErrType:
    REQUEST_PARAMS_ERROR = "RequestParamsError"
    CALL_COMFYUI_PROMPT_ERROR = "CallComfyUIPromptError"
    LOAD_PROGRESS_ERROR = "LoadProgressError"
    MARSHAL_RESULT_ERROR = "MarshalResultError"
    WEBSOCKET_UPGRADE_ERROR = "WebsocketUpgradeError"
    WEBSOCKET_WRITE_ERROR = "WebsocketWriteError"

class ErrMsg(Exception):
    def __init__(self, message: str, error: any):
        self.message = message
        self.error = error

    def __str__(self):
        return json.dumps({"message": self.message, "error": self.error})

def error_wrapper(err_type: str, err: Exception) -> ErrMsg:
    err_msg = str(err)

    if isinstance(err, HTTPError):
        err_msg = err.body

    try:
        err_obj = json.loads(err_msg)
    except json.JSONDecodeError:
        err_obj = err_msg

    return ErrMsg(message=err_type, error=err_obj)