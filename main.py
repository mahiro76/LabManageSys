"""实验室考勤管理系统 - 启动入口。

通过 `python main.py` 直接启动应用程序。
"""

from ui import Application


def main() -> None:
    """程序入口：创建 Application 实例并启动主循环。"""
    App = Application()
    App.Run()


if __name__ == "__main__":
    main()
