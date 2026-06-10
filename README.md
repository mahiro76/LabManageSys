# 实验室考勤管理系统 - 使用说明

##  快速开始

### 直接运行（推荐）

```bash
python main.py
```

**应用启动时会自动检测并拉起 MySQL 服务**，无需手动操作。

首次运行时会在控制台看到：
```
检测到 MySQL 未运行，正在自动启动...
[启动] MySQL 服务...
[OK] MySQL 启动成功
[OK] MySQL 自动启动成功
```

### 方式二：手动管理 MySQL

如果需要手动控制 MySQL 服务：

#### 启动 MySQL
```bash
python -c "from mysql_service import start_mysql; start_mysql()"
```

#### 停止 MySQL
```bash
python -c "from mysql_service import stop_mysql; stop_mysql()"
```

#### 查看状态
```bash
python -c "from mysql_service import print_status; print_status()"
```

#### 使用交互式守护进程
```bash
python mysql_daemon.py
# 然后根据提示选择：1=启动, 2=停止, 3=查看状态, 4=退出
```

---

##  默认登录凭据

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 员工 | `staff` | `staff123` |
| 学生 | `student` | `student123` |

---

##  项目结构

```
LabManageSys/
├── main.py              # 应用入口
── ui.py                # UI 层（Application + 5个功能页面）
├── db.py                # 数据访问层（MySqlManager）
├── models.py            # 数据模型 + 常量 + 验证工具
├── config.py            # 配置（MySQL 路径等）
├── mysql_service.py     # MySQL 本地服务管理
├── mysql_daemon.py      # MySQL 交互式守护进程
└── requirements.txt     # Python 依赖包
```

---

## ⚙️ 模块职责

| 模块 | 职责 |
|------|------|
| **main.py** | 应用入口，启动 Application |
| **ui.py** | 纯 UI 表现层，包含登录、5个功能 Tab 页面 |
| **db.py** | 业务数据访问层，封装所有数据库 CRUD 操作 |
| **models.py** | 数据模型定义、常量、验证工具函数 |
| **config.py** | MySQL 路径配置 |
| **mysql_service.py** | MySQL 本地服务的启动、停止、初始化等生命周期管理 |
| **mysql_daemon.py** | 交互式命令行工具，用于手动管理 MySQL |

---

## 🛠️ 常见问题

### Q: 应用启动时提示"无法连接数据库"？
A: 应用会自动尝试启动 MySQL。如果失败，请检查：
1. MySQL 安装路径是否正确（在 `config.py` 中配置 `MYSQL_HOME`）
2. 是否有权限启动 MySQL 服务
3. 端口 3306 是否被占用

可以手动启动 MySQL：
```bash
python -c "from mysql_service import start_mysql; start_mysql()"
```

### Q: 如何修改 MySQL 安装路径？
A: 编辑 `config.py` 文件，修改 `MYSQL_HOME` 变量：
```python
MYSQL_HOME = r"D:\mysql"  # Windows
# 或
MYSQL_HOME = "/opt/mysql"  # Linux/Mac
```

### Q: 如何重置 root 密码？
A: 编辑 `config.py` 中的 `NEW_ROOT_PASSWORD`，然后重新初始化：
```bash
python -c "from mysql_service import initialize_mysql; initialize_mysql(force=True)"
```

---

## 📊 功能特性

### 1. 角色权限管理
- ✅ **管理员（admin）**：拥有全部权限，可管理所有模块
- ✅ **普通老师（staff）**：可增删改查成员和考勤记录，查看统计图表
- ✅ **学生（student）**：仅可查看本人的基本信息和考勤记录

### 2. 成员档案管理
- ✅ 登记实验室成员信息：编号、姓名、性别、年龄、身份、职位、加入方式、联系方式、备注
- ✅ **数据校验**：手机号格式验证、年龄范围验证（10-80岁）、性别选项限制、必填字段检查
- ✅ **批量导入**：支持 Excel (.xlsx) 和 CSV (.csv) 文件导入，带逐行错误提示

### 3. 数据库设计
使用 MySQL 8.0+ 关系型数据库，包含四张表：
- `departments`（部门表）
- `members`（成员表）
- `attendance_records`（考勤记录表）
- `user_accounts`（用户账号表）

实现合理的表间关联和外键约束。

### 4. 考勤管理
- ✅ 记录每日考勤状态：正常、迟到、早退、请假
- ✅ 支持签到/签退时间记录
- ✅ 高级查询：按成员、日期范围、状态筛选
- ✅ **导出功能**：将考勤记录导出为 CSV 文件
- ✅ **重复检测**：同一成员同一天只能有一条考勤记录

### 5. 统计图表
- ✅ 考勤状态分布柱状图（正常/迟到/早退/请假）
- ✅ 各部门考勤记录数对比
- ✅ 基于 Matplotlib 实现，界面内嵌显示

### 6. 异常处理
- ✅ **数据库断连**：自动检测并提示用户
- ✅ **输入格式错误**：实时校验，友好提示
- ✅ **外键约束**：删除部门/成员时检查关联数据
- ✅ **重复数据**：主键冲突时给出明确提示

### 7. 系统集成与打包
- ✅ 使用 PyInstaller 打包为独立 exe 文件
- ✅ 自动启动 MySQL 服务（需配置 `mysql_service.py`）
- ✅ 首次运行自动初始化数据库和示例数据

---

## 💡 开发建议

1. **首次运行前**：确保已安装 MySQL 到指定路径
2. **生产环境**：建议使用独立的 MySQL 服务器，而非本地嵌入式服务
3. **备份数据**：定期备份 `D:\mysql\data` 目录（Windows）或 `/opt/mysql/data`（Linux/Mac）

---

## 📝 技术栈

- **前端**：Tkinter + ttk + Matplotlib
- **后端**：Python 3.10+
- **数据库**：MySQL 8.0+
- **ORM**：原生 SQL + mysql-connector-python
- **数据处理**：openpyxl（Excel）、csv（标准库）

---

**版本**：1.0  
**最后更新**：2026-06-10
