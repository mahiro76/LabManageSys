@echo off
echo ========================================
echo   Lab Manage System - Build Script
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/6] Checking Python environment...
python --version
echo.

echo [2/6] Cleaning old temp files...
if exist "build" rmdir /s /q "build" 2>nul

set BUILD_DIR=dist_build
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%" 2>nul
echo [OK] Cleaned
echo.

echo [3/6] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERR] Dependency installation failed
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo [4/6] Checking PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] PyInstaller not found, installing...
    python -m pip install pyinstaller
)
echo.

echo [5/6] Building executable...
python -m PyInstaller LabManageSys.spec -y --distpath %BUILD_DIR%
if errorlevel 1 (
    echo [ERR] Build failed
    pause
    exit /b 1
)
echo.

echo [6/6] Moving build output to dist\...
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "dist" (
    echo [WARN] dist folder locked, leaving output at %BUILD_DIR%\
    echo Output: %BUILD_DIR%\LabManageSys\LabManageSys.exe
) else (
    move /y "%BUILD_DIR%" "dist" >nul
    echo [OK] Build output moved to dist\LabManageSys\
)
echo.

echo ========================================
echo   Build Successful!
echo ========================================
echo.
if exist "dist\LabManageSys\LabManageSys.exe" (
    echo Output: dist\LabManageSys\LabManageSys.exe
) else (
    echo Output: %BUILD_DIR%\LabManageSys\LabManageSys.exe
)
echo.
pause