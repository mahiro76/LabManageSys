"""数据模型与工具函数。

定义所有数据类（DTO）、角色常量、验证函数等公共组件。
"""

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

ROLE_ADMIN = "admin"      # 管理员：拥有系统全部权限
ROLE_STAFF = "staff"      # 普通老师：可管理成员和考勤，但无数据库服务权限
ROLE_STUDENT = "student"  # 学生：仅可查看本人考勤记录

ATTENDANCE_STATUSES = ["正常", "迟到", "早退", "请假"]  # 考勤状态选项
GENDER_OPTIONS = ["男", "女"]                            # 性别选项
DEFAULT_DB_HOST = "localhost"    # 默认主机
DEFAULT_DB_PORT = "3306"         # 默认端口
DEFAULT_DB_USER = "root"         # 默认用户名
DEFAULT_DB_NAME = "lab_attendance_system"  # 默认数据库名
DEFAULT_DB_PASSWORD = "123456"   # 默认密码（与 config.py 中的 NEW_ROOT_PASSWORD 保持一致）

# 大陆手机号正则：1 开头的 11 位数字
DEFAULT_PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")


@dataclass
class DatabaseConfig:
    """数据库连接配置（数据传输对象）。"""
    Host: str       # 主机地址
    Port: int       # 端口号
    User: str       # 用户名
    Password: str   # 密码
    Database: str   # 数据库名


@dataclass
class LoginUser:
    """登录成功的用户信息（数据传输对象）。"""
    UserId: int           # 用户 ID
    Username: str         # 用户名
    Role: str             # 角色
    MemberId: str | None  # 关联的成员编号（可能为空）
    DisplayName: str      # 界面显示名


# 工具函数

def HashPassword(Password: str) -> str:
    """对密码进行 SHA-256 哈希，返回十六进制字符串。"""
    import hashlib
    return hashlib.sha256(Password.encode("utf-8")).hexdigest()


def IsValidPhone(Phone: str) -> bool:
    """校验手机号格式是否符合大陆 11 位手机号规范。"""
    return bool(DEFAULT_PHONE_PATTERN.fullmatch(Phone or ""))


def IsValidAge(AgeText: str) -> bool:
    """校验年龄是否为 10-80 之间的整数。"""
    if not AgeText:
        return False
    if not AgeText.isdigit():
        return False
    AgeValue = int(AgeText)
    return 10 <= AgeValue <= 80


def IsValidDate(DateText: str) -> bool:
    """校验日期字符串格式是否为 YYYY-MM-DD。"""
    try:
        datetime.strptime(DateText, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def IsValidTime(TimeText: str) -> bool:
    """校验时间字符串格式是否为 HH:MM:SS。允许为空字符串。"""
    if not TimeText:
        return True
    try:
        datetime.strptime(TimeText, "%H:%M:%S")
        return True
    except ValueError:
        return False


def NormalizeText(Value: Any) -> str:
    """将任意值转换为字符串并去除首尾空白；None 转换为空串。"""
    return str(Value).strip() if Value is not None else ""


def BuildNowText() -> str:
    """返回当前时间的格式化字符串 YYYY-MM-DD HH:MM:SS。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
