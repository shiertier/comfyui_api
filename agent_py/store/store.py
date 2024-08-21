from abc import ABC, abstractmethod

class Store(ABC):
    """
    KV 数据存储接口
    """

    @abstractmethod
    def save(self, key: str, value: str) -> None:
        """
        存储 value 到 key

        :param key: 键
        :param value: 值
        :return: 无返回值，如果存储失败则抛出异常
        """
        pass

    @abstractmethod
    def load(self, key: str) -> str:
        """
        从 key 加载 value

        :param key: 键
        :return: 值，如果加载失败则抛出异常
        """
        pass