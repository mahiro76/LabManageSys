# 实验室考勤管理系统 - PowerShell 自动打包脚本
# 使用方法：.\build.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  实验室考勤管理系统 - 自动打包脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 是否安装
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/6] 检查 Python 环境... $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未检测到 Python，请先安装 Python 3.8+" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""

# 清理旧文件
Write-Host "[2/6] 清理旧的打包文件..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "*.spec.bak") { Remove-Item -Force "*.spec.bak" }
Write-Host "清理完成" -ForegroundColor Green
Write-Host ""

# 安装依赖
Write-Host "[3/6] 安装/更新依赖包..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host "依赖安装完成" -ForegroundColor Green
Write-Host ""

# 检查 PyInstaller
Write-Host "[4/6] 检查 PyInstaller..." -ForegroundColor Yellow
try {
    pyinstaller --version | Out-Null
} catch {
    Write-Host "[警告] PyInstaller 未安装，正在安装..." -ForegroundColor Yellow
    pip install pyinstaller
}
Write-Host ""

# 开始打包
Write-Host "[5/6] 开始打包（这可能需要1-3分钟）..." -ForegroundColor Yellow
Write-Host "请稍候..." -ForegroundColor Gray
pyinstaller LabManageSys.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 打包失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
Write-Host ""

# 检查打包结果
Write-Host "[6/6] 检查打包结果..." -ForegroundColor Yellow
$exePath = "dist\LabManageSys\LabManageSys.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "[错误] 打包失败：未找到可执行文件" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  打包成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "可执行文件位置：" -ForegroundColor Cyan
Write-Host "  dist\LabManageSys\LabManageSys.exe" -ForegroundColor White
Write-Host ""

# 显示文件夹大小
$folderSize = (Get-ChildItem "dist\LabManageSys" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "文件夹大小：{0:N2} MB" -f $folderSize -ForegroundColor Cyan
Write-Host ""

Write-Host "提示：" -ForegroundColor Yellow
Write-Host "  1. 将整个 'dist\实验室考勤管理系统' 文件夹压缩为 ZIP" -ForegroundColor White
Write-Host "  2. 确保目标机器已安装并启动 MySQL 服务" -ForegroundColor White
Write-Host "  3. 首次运行可能需要几秒钟初始化" -ForegroundColor White
Write-Host ""

Read-Host "按回车键退出"
