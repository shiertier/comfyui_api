from pathlib import Path

class FSStore:
    """
    基于文件系统进行存储
    """

    def __init__(self, dir: str):
        """
        初始化文件系统存储

        :param dir: 存储目录
        """
        self.dir = Path(dir)

    def save(self, key: str, value: str) -> None:
        """
        存储 value 到 key

        :param key: 键
        :param value: 值
        :return: 无返回值，如果存储失败则抛出异常
        """
        fp = self.dir / key
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(value)

    def load(self, key: str) -> str:
        """
        从 key 加载 value

        :param key: 键
        :return: 值，如果加载失败则抛出异常
        """
        fp = self.dir / key
        if not fp.exists():
            raise FileNotFoundError(f"Key '{key}' not found")
        return fp.read_text()