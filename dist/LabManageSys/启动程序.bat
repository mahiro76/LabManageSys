@echo off
chcp 65001 >nul

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"

:: 启动程序
start "" "%SCRIPT_DIR%LabManageSys.exe"

exit /b 0
