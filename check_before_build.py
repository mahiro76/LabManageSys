"""
打包前环境检查脚本
使用方法：python check_before_build.py
"""

import sys
import subprocess
import importlib.util


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_python_version():
    """检查 Python 版本"""
    print_section("1. Python 版本检查")
    version = sys.version_info
    print(f"当前版本: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERR] Python 版本过低，需要 3.8+")
        return False
    
    print("[OK] Python 版本符合要求")
    return True


def check_package_installed(package_name, display_name=None):
    """检查包是否已安装"""
    if display_name is None:
        display_name = package_name
    
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f" [ERR] {display_name} 未安装")
        return False
    
    print(f"[OK] {display_name} 已安装")
    return True


def check_required_packages():
    """检查必需的依赖包"""
    print_section("2. 依赖包检查")
    
    packages = [
        ("mysql.connector", "MySQL连接器"),
        ("openpyxl", "Excel处理库"),
        ("matplotlib", "图表库"),
        ("pyinstaller", "打包工具"),
    ]
    
    all_ok = True
    for package, name in packages:
        if not check_package_installed(package, name):
            all_ok = False
    
    return all_ok


def check_mysql_service():
    """检查 MySQL 服务状态"""
    print_section("3. MySQL 服务检查")
    
    try:
        result = subprocess.run(
            ["net", "start"],
            capture_output=True,
            text=True,
            encoding="gbk"
        )
        
        if "MySQL" in result.stdout:
            print("[OK] MySQL 服务正在运行")
            return True
        else:
            print("[WARN] MySQL 服务未运行（打包时可以停止）")
            return True  # 打包时不需要MySQL运行
    except Exception as e:
        print(f"[WARN] 无法检查 MySQL 状态: {e}")
        return True


def check_project_files():
    """检查项目文件完整性"""
    print_section("4. 项目文件检查")
    
    import os
    
    required_files = [
        "main.py",
        "ui.py",
        "db.py",
        "models.py",
        "config.py",
        "mysql_service.py",
        "LabManageSys.spec",
        "requirements.txt",
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f" [ERR] {file} 不存在")
            all_exist = False
    
    return all_exist


def check_clean_environment():
    """检查是否有旧的打包文件"""
    print_section("5. 环境清理检查")
    
    import os
    import shutil
    
    old_dirs = ["build", "dist"]
    found_old = False
    
    for dir_name in old_dirs:
        if os.path.exists(dir_name):
            print(f"[WARN] 发现旧的 {dir_name} 目录")
            found_old = True
    
    if not found_old:
        print("[OK] 环境干净，无旧文件")
        return True
    
    response = input("\n是否自动清理？(y/n): ").strip().lower()
    if response == 'y':
        for dir_name in old_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"[OK] 已删除 {dir_name}")
        return True
    else:
        print("[WARN] 建议手动清理后再打包")
        return True


def run_tests():
    """运行基本功能测试"""
    print_section("6. 基本功能测试")
    
    try:
        # 测试导入
        print("测试模块导入...")
        from models import DatabaseConfig, ROLE_ADMIN
        from db import MySqlManager
        
        print("[OK] 模块导入成功")
        
        # 测试数据库配置
        print("测试数据库配置...")
        config = DatabaseConfig("localhost", 3306, "root", "123456", "test_db")
        assert config.Host == "localhost"
        assert config.Port == 3306
        
        print("[OK] 数据库配置正常")
        
        return True
    except Exception as e:
        print(f"[ERR] 功能测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  实验室考勤管理系统 - 打包前环境检查")
    print("=" * 60)
    
    checks = [
        ("Python 版本", check_python_version),
        ("依赖包", check_required_packages),
        ("MySQL 服务", check_mysql_service),
        ("项目文件", check_project_files),
        ("环境清理", check_clean_environment),
        ("功能测试", run_tests),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERR] {name} 检查出错: {e}")
            results.append((name, False))
        
    # 汇总结果
    print_section("检查结果汇总")
        
    all_passed = True
    for name, result in results:
        status = "[OK]" if result else "[ERR]"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
        
    print("\n" + "=" * 60)
    if all_passed:
        print("[OK] 所有检查通过！可以开始打包了")
        print("\n推荐操作：")
        print("  Windows CMD:   build.bat")
        print("  PowerShell:    .\\build.ps1")
        print("  手动打包:      pyinstaller LabManageSys.spec")
    else:
        print("[WARN] 部分检查未通过，请先修复问题再打包")
    print("=" * 60 + "\n")
        
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
