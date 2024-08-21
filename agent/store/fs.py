from pathlib import Path

class FS:
    """基于文件系统进行存储"""

    def __init__(self, dir: str):
        self.dir = Path(dir)

    def save(self, key: str, value: str) -> None:
        """存储数据"""
        fp = self.dir / key  # 使用 `/` 操作符连接路径

        fp.parent.mkdir(parents=True, exist_ok=True)  # 创建必要的父目录
        fp.write_text(value)  # 直接写入文本

    def load(self, key: str) -> str:
        """加载数据"""
        fp = self.dir / key  # 使用 `/` 操作符连接路径
        if not fp.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return fp.read_text()  # 读取文本内容
