from abc import ABC, abstractmethod

class Store(ABC):
    @abstractmethod
    def save(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> str:
        pass
