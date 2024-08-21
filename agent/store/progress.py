import json
from dataclasses import dataclass, field
from typing import List

class Progress:
    """出图进度状态存储"""

    def __init__(self, store):
        self.store = store

    def save_progress(self, key: str, progress: 'TProgress') -> None:
        """保存状态到存储"""
        self.store.save(key, progress.to_json())

    def load_progress(self, key: str) -> 'TProgress':
        """从存储加载状态"""
        value = self.store.load(key)
        progress = TProgress()
        progress.from_json(value)
        return progress

class TProgress(dict):
    """进度状态"""

    def to_json(self) -> str:
        """转换 TProgress 到 JSON 字符串"""
        return json.dumps(self)

    def from_json(self, json_str: str) -> None:
        """从 JSON 字符串加载 TProgress"""
        if json_str:
            self.update(json.loads(json_str))

@dataclass
class TProgressNodeImage:
    filename: str
    subfolder: str
    type: str  # Type must be "image"

@dataclass
class TProgressNode:
    max: int
    value: int
    start: int
    last_updated: int
    images: List[TProgressNodeImage] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
