"""应用全局配置。

包含 MySQL 本地服务路径配置和数据库连接默认值。
"""

import os
import platform

sysInfo = platform.system()  # 当前操作系统类型（如 "Windows" / "Linux"）

# ==================== MySQL 本地服务路径 ====================
MYSQL_HOME = r"D:\mysql" if sysInfo == "Windows" else "/opt/mysql"
MYSQL_DATA = os.path.join(MYSQL_HOME, "data")
MYSQL_CONF = os.path.join(MYSQL_HOME, "my.ini" if sysInfo == "Windows" else "my.cnf")
MYSQL_LOG = os.path.join(MYSQL_HOME, "mysql.log")
PID_FILE = os.path.join(MYSQL_HOME, "mysql.pid")
STATE_FILE = os.path.join(MYSQL_HOME, "mysql_setup_state.json")
MYSQL_PORT = 3306
NEW_ROOT_PASSWORD = "123456"   # 请修改为你想要的 root 密码
# ============================================================


def get_mysqld_path() -> str:
    """获取 mysqld（MySQL 服务端）可执行文件的完整路径。"""
    return os.path.join(MYSQL_HOME, "bin", "mysqld.exe" if sysInfo == "Windows" else "mysqld")


def get_mysql_path() -> str:
    """获取 mysql（MySQL 客户端）可执行文件的完整路径。"""
    return os.path.join(MYSQL_HOME, "bin", "mysql.exe" if sysInfo == "Windows" else "mysql")


def get_mysqladmin_path() -> str:
    """获取 mysqladmin（MySQL 管理工具）可执行文件的完整路径。"""
    return os.path.join(MYSQL_HOME, "bin", "mysqladmin.exe" if sysInfo == "Windows" else "mysqladmin")
