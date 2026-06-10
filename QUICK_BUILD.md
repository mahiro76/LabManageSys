#  打包快速参考卡

## 一键打包（推荐）

### Windows CMD
```bash
build.bat
```

### PowerShell
```powershell
.\build.ps1
```

---

## 手动打包

```bash
pyinstaller LabManageSys.spec
```

---

## 打包结果

```
dist\实验室考勤管理系统\
── 实验室考勤管理系统.exe      # 主程序（50-80 MB）
├── python312.dll               # Python运行时
└── _internal\                  # 所有依赖（~100 MB）
    ├── mysql\                  # MySQL连接器
    ├── openpyxl\               # Excel库
    ├── matplotlib\             # 图表库
    └── ...                     # 其他依赖
```

**总大小**: 150-250 MB（含完整Python环境）

---

## 分发步骤

1. ✅ 压缩整个 `dist\实验室考勤管理系统\` 文件夹为 ZIP
2. ✅ 发送给用户
3. ✅ 用户解压后双击 `.exe` 运行

⚠️ **目标机器需安装 MySQL 服务！**

---

## 常见问题

### Q: 打包后体积太大？
A: 已在配置中启用 UPX 压缩，可减少 30-50% 体积

### Q: 如何添加图标？
A: 准备 `app.ico`，修改 `LabManageSys.spec` 第56行：`icon='app.ico'`

### Q: 打包失败？
A: 使用 `pyinstaller --console LabManageSys.spec` 查看错误信息

### Q: 缺少某个模块？
A: 在 `LabManageSys.spec` 的 `hiddenimports` 中添加该模块名

---

## 详细文档

-  [BUILD_GUIDE.md](BUILD_GUIDE.md) - 完整打包指南
-  [PACKAGING.md](PACKAGING.md) - PyInstaller 配置说明

---

**最后更新**: 2026-06-10
