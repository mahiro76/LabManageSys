"""MySQL 本地守护进程管理服务。

提供 MySQL 本地服务的初始化、启动、停止、配置等完整生命周期管理。
"""

import json
import os
import re
import shutil
import socket
import subprocess
import time
from typing import Any

from config import (
    MYSQL_DATA, MYSQL_CONF, MYSQL_LOG, PID_FILE, STATE_FILE, MYSQL_PORT,
    NEW_ROOT_PASSWORD, sysInfo,
    get_mysqld_path, get_mysql_path, get_mysqladmin_path,
)


# ---- 底层工具函数 ----


def run_command(cmd, capture_output=True, check=False, input_text=None):
    """运行 shell 命令并返回 (returncode, stdout, stderr)。"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd, shell=(sysInfo == "Windows"),
                capture_output=True, text=True, input=input_text, check=check
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        else:
            subprocess.run(cmd, shell=(sysInfo == "Windows"), check=check)
            return 0, "", ""
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else ""


def load_state() -> dict:
    """从状态文件加载 MySQL 部署状态。"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "initialized": False,
        "password_set": False,
        "started": False,
        "configured": False,
    }


def save_state(state: dict) -> None:
    """保存 MySQL 部署状态到文件。"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def is_mysql_running() -> bool:
    """检测 MySQL 服务是否正在运行。"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = f.read().strip()
        except Exception:
            pid = ''
        if pid.isdigit():
            if sysInfo == "Windows":
                ret, out, _ = run_command(f'tasklist /FI "PID eq {pid}"')
                if ret == 0 and str(pid) in out and "mysqld" in out:
                    return True
            else:
                try:
                    os.kill(int(pid), 0)
                    return True
                except OSError:
                    pass
    try:
        with socket.create_connection(('127.0.0.1', MYSQL_PORT), timeout=2):
            return True
    except Exception:
        return False
    return False


def wait_for_mysql_start(timeout: int = 30) -> bool:
    """等待 MySQL 服务启动，最多等待 timeout 秒。"""
    start = time.time()
    while time.time() - start < timeout:
        if is_mysql_running():
            return True
        time.sleep(1)
    return False


def get_temp_root_password() -> str | None:
    """从 MySQL 错误日志中提取临时 root 密码。"""
    error_log = os.path.join(MYSQL_HOME, "mysql-error.log")
    if not os.path.exists(error_log):
        error_log = MYSQL_LOG
    if not os.path.exists(error_log):
        return None
    with open(error_log, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    match = re.search(r"temporary password.*?:\s+(\S+)", content, re.IGNORECASE)
    return match.group(1) if match else None


# ---- 核心生命周期管理 ----


def initialize_mysql(force: bool = False) -> bool:
    """初始化 MySQL 数据目录。"""
    state = load_state()
    if state.get("initialized") and not force:
        print("[OK] 数据目录已初始化，跳过")
        return True
    print("[初始化] MySQL 数据目录...")
    mysqld = get_mysqld_path()
    if not os.path.exists(mysqld):
        print(f"[ERR] 找不到 mysqld: {mysqld}")
        return False
    if os.path.exists(MYSQL_DATA) and os.listdir(MYSQL_DATA):
        if not force:
            print(f"[ERR] 数据目录 {MYSQL_DATA} 非空，请先删除或使用 --force")
            return False
        print(f"[WARN] 强制模式：删除现有数据目录 {MYSQL_DATA}")
        shutil.rmtree(MYSQL_DATA)
    os.makedirs(MYSQL_DATA, exist_ok=True)
    cmd = [mysqld, "--initialize", "--console"]
    if os.path.exists(MYSQL_CONF):
        cmd.insert(1, f"--defaults-file={MYSQL_CONF}")
    ret, stdout, stderr = run_command(cmd, capture_output=False)
    time.sleep(2)
    temp_pwd = get_temp_root_password()
    if temp_pwd:
        print(f"[OK] MySQL 初始化完成，临时 root 密码已生成")
        print(f"  临时密码: {temp_pwd}")
        state["temp_password"] = temp_pwd
    else:
        print("[WARN] 未找到临时密码，请检查日志文件")
        state["temp_password"] = None
    state["initialized"] = True
    save_state(state)
    return True


def set_root_password(force: bool = False) -> bool:
    """修改 MySQL root 密码为 NEW_ROOT_PASSWORD。"""
    state = load_state()
    if state.get("password_set") and not force:
        print("[OK] root 密码已修改，跳过")
        return True
    if not state.get("initialized"):
        print("[ERR] 数据目录未初始化，请先执行初始化")
        return False
    if not is_mysql_running():
        print("⏳ MySQL 未运行，正在启动...")
        if not start_mysql():
            print("[ERR] 无法启动 MySQL，不能修改密码")
            return False
        if not wait_for_mysql_start():
            print("[ERR] MySQL 启动超时")
            return False
    temp_pwd = state.get("temp_password") or get_temp_root_password()
    if not temp_pwd:
        print("[ERR] 未找到临时 root 密码，无法修改密码")
        return False
    mysql_client = get_mysql_path()
    sql = f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{NEW_ROOT_PASSWORD}'; FLUSH PRIVILEGES;"
    cmd = [mysql_client, "-u", "root", f"-p{temp_pwd}", "--connect-expired-password", "-e", sql]
    ret, stdout, stderr = run_command(cmd, capture_output=True)
    if ret != 0:
        print(f"[ERR] 修改 root 密码失败: {stderr}")
        return False
    print("[OK] root 密码修改成功")
    state["password_set"] = True
    state.pop("temp_password", None)
    save_state(state)
    return True


def start_mysql(force: bool = False) -> bool:
    """启动 MySQL 服务。"""
    state = load_state()
    if is_mysql_running():
        print("[OK] MySQL 已在运行")
        state["started"] = True
        save_state(state)
        return True
    if not state.get("initialized"):
        print("[ERR] 数据目录未初始化，请先初始化")
        return False
    print("[启动] MySQL 服务...")
    mysqld = get_mysqld_path()
    if not os.path.exists(mysqld):
        print(f"[ERR] 找不到 mysqld: {mysqld}")
        return False
    cmd = [mysqld]
    if os.path.exists(MYSQL_CONF):
        cmd.append(f"--defaults-file={MYSQL_CONF}")
    cmd.append(f"--datadir={MYSQL_DATA}")
    with open(MYSQL_LOG, "a") as log:
        startupinfo = None
        creationflags = 0
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
            if hasattr(subprocess, "DETACHED_PROCESS"):
                creationflags |= subprocess.DETACHED_PROCESS
        except Exception:
            startupinfo = None
            creationflags = 0
        if sysInfo == "Windows":
            proc = subprocess.Popen(
                cmd, stdout=log, stderr=subprocess.STDOUT,
                startupinfo=startupinfo, creationflags=creationflags,
            )
        else:
            proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, preexec_fn=os.setsid)
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))
    if wait_for_mysql_start():
        print("[OK] MySQL 启动成功")
        state["started"] = True
        save_state(state)
        return True
    print("[ERR] MySQL 启动超时，请检查日志:", MYSQL_LOG)
    return False


def stop_mysql() -> bool:
    """停止 MySQL 服务。"""
    if not is_mysql_running():
        print("MySQL 未运行")
        return True
    mysqladmin = get_mysqladmin_path()
    cmd = [mysqladmin, "-u", "root", f"-p{NEW_ROOT_PASSWORD}", "shutdown"]
    ret, _, stderr = run_command(cmd, capture_output=True)
    if ret != 0:
        print(f"[ERR] 停止 MySQL 失败: {stderr}")
        return False
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    state = load_state()
    state["started"] = False
    save_state(state)
    print("[OK] MySQL 已停止")
    return True


def configure_mysql(force: bool = False) -> bool:
    """创建额外数据库和用户。"""
    state = load_state()
    if state.get("configured") and not force:
        print("[OK] 额外配置已完成，跳过")
        return True
    if not state.get("password_set"):
        print("[ERR] root 密码未设置，无法进行额外配置")
        return False
    if not is_mysql_running():
        print("[ERR] MySQL 未运行，请先启动")
        return False
    sql = """
    CREATE DATABASE IF NOT EXISTS myapp;
    CREATE USER IF NOT EXISTS 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
    GRANT ALL PRIVILEGES ON myapp.* TO 'myuser'@'localhost';
    FLUSH PRIVILEGES;
    """
    mysql_client = get_mysql_path()
    cmd = [mysql_client, "-u", "root", f"-p{NEW_ROOT_PASSWORD}", "-e", sql]
    ret, _, stderr = run_command(cmd, capture_output=True)
    if ret != 0:
        print(f"[ERR] 额外配置失败: {stderr}")
        return False
    print("[OK] 额外配置完成（创建数据库 myapp 和用户 myuser）")
    state["configured"] = True
    save_state(state)
    return True


# ---- 组合操作 ----


def full_setup() -> bool:
    """完整部署 MySQL：初始化 → 启动 → 改密 → 额外配置。"""
    steps = [
        ("initialized", initialize_mysql),
        ("started", start_mysql),
        ("password_set", set_root_password),
        ("configured", configure_mysql),
    ]
    for step_name, step_func in steps:
        print(f"\n--- 检查步骤: {step_name} ---")
        if not step_func(force=False):
            print(f"✗ 步骤 {step_name} 失败，中止")
            return False
    print("\n🎉 MySQL 完整部署成功！")
    return True


def force_step(step_name: str) -> bool:
    """强制重做指定步骤。"""
    state = load_state()
    if step_name == "all":
        state = {k: False for k in state if not k.startswith("temp")}
        save_state(state)
        return full_setup()
    elif step_name == "initialized":
        initialize_mysql(force=True)
    elif step_name == "started":
        stop_mysql()
        start_mysql(force=True)
    elif step_name == "password_set":
        state["password_set"] = False
        save_state(state)
        set_root_password(force=True)
    elif step_name == "configured":
        state["configured"] = False
        save_state(state)
        configure_mysql(force=True)
    else:
        print(f"未知步骤: {step_name}")
        return False
    return True


def print_status() -> None:
    """打印 MySQL 部署状态。"""
    state = load_state()
    print("========== MySQL 部署状态 ==========")
    print(f"初始化 (initialized): {state.get('initialized', False)}")
    print(f"密码已修改 (password_set): {state.get('password_set', False)}")
    print(f"服务运行中 (started): {is_mysql_running()}")
    print(f"额外配置 (configured): {state.get('configured', False)}")
    if is_mysql_running():
        print(f"端口: {MYSQL_PORT}")
        print(f"PID 文件: {PID_FILE}")
    print("===================================")


__all__ = [
    "initialize_mysql", "set_root_password", "start_mysql", "stop_mysql",
    "configure_mysql", "full_setup", "force_step", "print_status",
    "is_mysql_running", "run_command", "load_state", "save_state",
    "wait_for_mysql_start", "get_temp_root_password",
]
