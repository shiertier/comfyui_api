from abc import ABC, abstractmethod

class Store(ABC):
    """Store KV 数据存储"""

    @abstractmethod
    def save(self, key: str, value: str) -> None:
        """存储 value 到 key"""
        pass

    @abstractmethod
    def load(self, key: str) -> str:
        """从 key 加载 value"""
        pass
