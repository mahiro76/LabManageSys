@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   实验室考勤管理系统 - 自动打包脚本
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/6] 检查 Python 环境...
python --version
echo.

:: 清理旧文件
echo [2/6] 清理旧的打包文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec.bak" del /f /q "*.spec.bak"
echo 清理完成
echo.

:: 安装依赖
echo [3/6] 安装/更新依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo 依赖安装完成
echo.

:: 检查 PyInstaller
echo [4/6] 检查 PyInstaller...
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] PyInstaller 未安装，正在安装...
    pip install pyinstaller
)
echo.

:: 开始打包
echo [5/6] 开始打包（这可能需要1-3分钟）...
echo 请稍候...
pyinstaller LabManageSys.spec
if %errorlevel% neq 0 (
    echo [错误] 打包失败
    pause
    exit /b 1
)
echo.

:: 检查打包结果
echo [6/6] 检查打包结果...
if not exist "dist\LabManageSys\LabManageSys.exe" (
    echo [错误] 打包失败：未找到可执行文件
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包成功！
echo ========================================
echo.
echo 可执行文件位置：
echo   dist\LabManageSys\LabManageSys.exe
echo.
echo 文件夹大小：
dir "dist\LabManageSys" | findstr "个文件"
echo.
echo 提示：
echo   1. 将整个 "dist\LabManageSys" 文件夹压缩为 ZIP
echo   2. 确保目标机器已安装并启动 MySQL 服务
echo   3. 首次运行可能需要几秒钟初始化
echo.

pause
