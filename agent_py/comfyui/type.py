from typing import Dict, Any, List

class TPromptNode:
    def __init__(self, inputs: Dict[str, Any], class_type: str, meta: Dict[str, Any]):
        self.inputs = inputs
        self.class_type = class_type
        self.meta = meta

class TPrompt(Dict[str, TPromptNode]):
    pass

class TPromptResponse:
    def __init__(self, prompt_id: str):
        self.prompt_id = prompt_id

class TWebsocketMessage:
    def __init__(self, type: str, data: 'TWebsocketMessageData'):
        self.type = type
        self.data = data

class TWebsocketMessageData:
    def __init__(self, sid: str, prompt_id: str, status: 'TWebsocketMessageStatus', nodes: List[str], node: str, max: int, value: int, output: 'TWebsocketMessageOutput'):
        self.sid = sid
        self.prompt_id = prompt_id
        self.status = status
        self.nodes = nodes
        self.node = node
        self.max = max
        self.value = value
        self.output = output

class TWebsocketMessageStatus:
    def __init__(self, queue_remaining: int):
        self.exec_info = {
            "queue_remaining": queue_remaining
        }

class TWebsocketMessageOutput:
    def __init__(self, images: List['TWebsocketMessageOutputImage'], tags: List[str]):
        self.images = images
        self.tags = tags

class TWebsocketMessageOutputImage:
    def __init__(self, filename: str, name: str, subfolder: str, type: str):
        self.filename = filename
        self.name = name
        self.subfolder = subfolder
        self.type = type