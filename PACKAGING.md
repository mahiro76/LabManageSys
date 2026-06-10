# 实验室考勤管理系统 - 打包指南

## 前置要求

1. **Python 环境**：Python 3.8+（推荐 3.10+）
2. **依赖包已安装**：`pip install -r requirements.txt`
3. **PyInstaller 已安装**：已在 `requirements.txt` 中声明

## 打包步骤

### 方法一：使用 .spec 文件（推荐）

```bash
pyinstaller LabManageSys.spec
```

打包完成后，可执行文件位于：
- `dist\实验室考勤管理系统\实验室考勤管理系统.exe`

### 方法二：使用命令行参数

```bash
pyinstaller --onefile --windowed --name="实验室考勤管理系统" ^
    --hidden-import=mysql.connector ^
    --hidden-import=openpyxl ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    main.py
```

生成的单文件 exe 位于：`dist\实验室考勤管理系统.exe`

## 注意事项

### 1. MySQL 服务依赖

打包后的程序**仍然需要本地 MySQL 服务运行**。如果目标机器没有安装 MySQL：

- **方案 A**：在目标机器上安装 MySQL 8.0+
- **方案 B**：将 MySQL 嵌入到安装包中（需要额外配置，较复杂）

### 2. 数据库初始化

首次运行时，程序会自动：
1. 检测并启动 MySQL 服务（如果配置了 `mysql_service.py`）
2. 创建数据库 `lab_attendance_system`
3. 创建表结构
4. 插入示例数据

### 3. 默认登录账号

系统预置了三个测试账号：

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 全部权限 |
| staff | staff123 | 普通老师 | 增删改查 + 统计 |
| student | student123 | 学生 | 仅查看本人考勤 |

### 4. 图标定制（可选）

如果需要自定义应用图标：

1. 准备 `.ico` 格式的图标文件（建议 256x256 像素）
2. 修改 `LabManageSys.spec` 中的 `icon` 参数：
   ```python
   icon='app.ico'
   ```
3. 重新打包

### 5. 减小体积（可选）

如果使用 `--onefile` 模式，exe 文件会较大（约 100-200 MB）。如需减小体积：

- 使用 `--onedir` 模式（默认），生成文件夹而非单文件
- 排除不必要的模块（如 matplotlib 的某些后端）
- 使用 UPX 压缩（已在 spec 文件中启用）

## 常见问题

### Q1: 打包后运行闪退？

**A**: 可能是缺少依赖或路径问题。解决方法：

1. 使用 `--console` 模式打包，查看错误信息：
   ```bash
   pyinstaller --console LabManageSys.spec
   ```
2. 检查 `dist` 目录下的日志文件

### Q2: 提示找不到 MySQL？

**A**: 确保目标机器已安装并启动 MySQL 服务。检查方法：

```bash
# Windows
net start | findstr MySQL

# 或手动启动
net start MySQL80
```

### Q3: Excel 导入失败？

**A**: 确保 Excel 文件格式正确：

- 第一行为表头（列名）
- 列顺序：member_id, name, gender, age, identity, position, join_method, contact, note
- 手机号格式：11位数字，以1开头
- 年龄范围：10-80

### Q4: CSV 导入乱码？

**A**: 确保 CSV 文件使用 UTF-8 编码（带 BOM），保存时选择 "UTF-8 with BOM" 或 "UTF-8-SIG"。

## 分发建议

### 完整分发包结构

```
实验室考勤管理系统/
├── 实验室考勤管理系统.exe      # 主程序
├── README.md                   # 使用说明
├── 示例数据.xlsx               # Excel 导入模板
└── 数据库说明.txt              # MySQL 安装指南
```

### 简化版（单文件）

如果使用 `--onefile` 模式，只需分发单个 exe 文件，但用户需自行安装 MySQL。

## 更新日志

- v1.0 (2026-06-10)
  - 初始版本发布
  - 支持角色权限控制（admin/staff/student）
  - 支持 Excel/CSV 批量导入
  - 自动启动 MySQL 服务
  - 增强异常处理和用户提示
