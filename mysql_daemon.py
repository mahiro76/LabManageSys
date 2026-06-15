"""交互式 MySQL 守护进程。

提供交互菜单让用户选择启动/停止/查看状态/初始化 MySQL，
并在程序退出时自动关闭数据库。
通过 `python mysql_daemon.py` 启动。
"""

import sys
import signal
from mysql_service import start_mysql, stop_mysql, print_status, is_mysql_running, initialize_mysql


def cleanup():
    """清理函数：若 MySQL 正在运行则自动停止。"""
    try:
        if is_mysql_running():
            print("\n检测到 MySQL 正在运行，正在停止...")
            stop_mysql()
        else:
            print("\nMySQL 未运行，无需停止。")
    except Exception as e:
        print(f"清理时发生异常: {e}")


def handle_signal(signum, frame):
    """信号处理器：收到 SIGINT/SIGTERM 时执行清理后退出。"""
    print(f"\n收到信号 {signum}，正在退出并关闭 MySQL（如果正在运行）...")
    cleanup()
    sys.exit(0)


def menu():
    """打印交互菜单选项。"""
    print("\n=== MySQL 守护进程交互菜单 ===")
    print("1) 启动 MySQL")
    print("2) 停止 MySQL")
    print("3) 查看状态")
    print("4) 初始化数据目录（首次使用必选）")
    print("5) 退出（退出时自动停止 MySQL）")


def main():
    """主循环：注册信号处理器，循环显示菜单，处理用户选择。"""
    # 注册信号处理，确保 Ctrl+C / 终止信号时能清理
    try:
        signal.signal(signal.SIGINT, handle_signal)
    except Exception:
        pass
    try:
        signal.signal(signal.SIGTERM, handle_signal)
    except Exception:
        pass

    try:
        while True:
            menu()
            try:
                choice = input("请选择操作 [1-4]: ").strip()
            except (EOFError, KeyboardInterrupt):
                # 用户按 Ctrl+D / Ctrl+C 或输入流结束
                break
            if choice == "1":
                print("开始启动 MySQL...")
                start_mysql()
            elif choice == "2":
                print("开始停止 MySQL...")
                stop_mysql()
            elif choice == "3":
                print_status()
            elif choice == "4":
                print("开始初始化 MySQL 数据目录...")
                result = initialize_mysql(force=False)
                if result:
                    print("✓ 初始化成功！现在可以启动 MySQL 了")
                else:
                    print(" 初始化失败，请检查日志")
            elif choice == "5":
                print("退出程序，准备关闭 MySQL（如在运行）...")
                break
            else:
                print("无效选择，请重试。")
    finally:
        cleanup()
        print("已退出。")


if __name__ == "__main__":
    main()
