from abc import ABC, abstractmethod
from pathlib import Path

class Store(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> str:
        pass

class FSStore:
    """
    基于文件系统进行存储
    """
    def __init__(self, dir: str):
        self.dir = Path(dir)

    def save(self, key: str, value: str) -> None:
        fp = self.dir / key
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(value)

    def load(self, key: str) -> str:
        fp = self.dir / key
        if not fp.exists():
            raise FileNotFoundError(f"Key '{key}' not found")
        return fp.read_text()