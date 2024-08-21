import json
from typing import Dict, List, Optional
from .store import Store

class TProgressNodeImage:
    def __init__(self, filename: str, subfolder: str, type: str):
        self.filename = filename
        self.subfolder = subfolder
        self.type = type

    def to_dict(self):
        return {
            "filename": self.filename,
            "subfolder": self.subfolder,
            "type": self.type
        }

    @staticmethod
    def from_dict(data: dict):
        return TProgressNodeImage(
            filename=data["filename"],
            subfolder=data["subfolder"],
            type=data["type"]
        )

class TProgressNode:
    def __init__(self, max: int, value: int, start: int, last_updated: int, images: List[TProgressNodeImage], results: Optional[List[str]] = None):
        self.max = max
        self.value = value
        self.start = start
        self.last_updated = last_updated
        self.images = images
        self.results = results or []

    def to_dict(self):
        return {
            "max": self.max,
            "value": self.value,
            "start": self.start,
            "last_updated": self.last_updated,
            "images": [image.to_dict() for image in self.images],
            "results": self.results
        }

    @staticmethod
    def from_dict(data: dict):
        return TProgressNode(
            max=data["max"],
            value=data["value"],
            start=data["start"],
            last_updated=data["last_updated"],
            images=[TProgressNodeImage.from_dict(image) for image in data["images"]],
            results=data.get("results", [])
        )

class TProgress(Dict[str, TProgressNode]):
    def to_json(self) -> str:
        return json.dumps({key: value.to_dict() for key, value in self.items()})

    @staticmethod
    def from_json(json_str: str) -> 'TProgress':
        data = json.loads(json_str)
        progress = TProgress()
        for key, value in data.items():
            progress[key] = TProgressNode.from_dict(value)
        return progress

class Progress:
    def __init__(self, store: 'Store'):
        self.store = store

    def save_progress(self, key: str, progress: TProgress) -> None:
        self.store.save(key, progress.to_json())

    def load_progress(self, key: str) -> TProgress:
        value = self.store.load(key)
        return TProgress.from_json(value)