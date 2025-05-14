from pathlib import Path
from typing import Any


class ProjectPaths:
    """
    此类的目的是为了更好地管理不同项目的路径导入
    """
    # 获取项目根目录
    _ROOT = Path(__file__).resolve().parent.parent.parent

    def __init__(self):
        """
        初始化项目路径
        """
        self._log = "logs"
        self._data = "data"
        self._cookies = "cookies"
        self._config = "config"
        self._src = "src"

        # 初始化文件夹
        self._init_dir()

    def _init_dir(self):
        """
        判断文件夹是否存在，不存在则创建
        """
        if not self.LOGS.exists():
            self.LOGS.mkdir()
        if not self.DATA.exists():
            self.DATA.mkdir()
        if not self.COOKIES.exists():
            self.COOKIES.mkdir()
        if not self.CONFIG.exists():
            self.CONFIG.mkdir()

    @property
    def LOGS(self):
        return self._ROOT / self._log

    @property
    def CONFIG(self):
        return self._ROOT / self._config

    @property
    def DATA(self):
        return self._ROOT / self._data

    @property
    def COOKIES(self):
        return self._ROOT / self._cookies

    @property
    def SRC(self):
        return self._ROOT / self._src

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        返回项目根目录
        """
        return self._ROOT


if __name__ == '__main__':
    test = ProjectPaths()
    print(test.LOGS)
    print(test())
