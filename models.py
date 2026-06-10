from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"
ROLE_STUDENT = "student"

ATTENDANCE_STATUSES = ["正常", "迟到", "早退", "请假"]
GENDER_OPTIONS = ["男", "女"]
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = "3306"
DEFAULT_DB_USER = "root"
DEFAULT_DB_NAME = "lab_attendance_system"
DEFAULT_DB_PASSWORD = "123456"  # 与 config.py 中的 NEW_ROOT_PASSWORD 保持一致
DEFAULT_PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")


@dataclass
class DatabaseConfig:
    Host: str
    Port: int
    User: str
    Password: str
    Database: str


@dataclass
class LoginUser:
    UserId: int
    Username: str
    Role: str
    MemberId: str | None
    DisplayName: str


# 工具函数

def HashPassword(Password: str) -> str:
    import hashlib
    return hashlib.sha256(Password.encode("utf-8")).hexdigest()


def IsValidPhone(Phone: str) -> bool:
    return bool(DEFAULT_PHONE_PATTERN.fullmatch(Phone or ""))


def IsValidAge(AgeText: str) -> bool:
    if not AgeText:
        return False
    if not AgeText.isdigit():
        return False
    AgeValue = int(AgeText)
    return 10 <= AgeValue <= 80


def IsValidDate(DateText: str) -> bool:
    try:
        datetime.strptime(DateText, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def IsValidTime(TimeText: str) -> bool:
    if not TimeText:
        return True
    try:
        datetime.strptime(TimeText, "%H:%M:%S")
        return True
    except ValueError:
        return False


def NormalizeText(Value: Any) -> str:
    return str(Value).strip() if Value is not None else ""


def BuildNowText() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
