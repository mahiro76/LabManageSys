# 实验室考勤管理系统

实验室成员信息与考勤管理的桌面应用程序，支持多角色权限控制、Excel/CSV 批量导入、考勤统计可视化。

## 功能特性

### 1. 角色权限管理
| 角色 | 权限范围 |
|------|---------|
| **管理员（admin）** | 全部权限：部门/成员/考勤/用户的增删改查、统计图表、重置用户密码 |
| **普通老师（staff）** | 部门/成员/统计的增删改查；考勤仅查看，无用户管理权限 |
| **学生（student）** | 仅查看本人的基本信息和考勤记录 |

### 2. 成员档案管理
- 登记 9 个字段：编号、姓名、性别、年龄、身份、职位、加入方式、联系方式、备注
- 数据校验：手机号正则（11 位 / 1 开头）、年龄范围（10-80）、性别限制、必填项检查
- 批量导入：支持 Excel (.xlsx) 和 CSV (.csv)，逐行校验并汇总错误提示

### 3. 考勤管理
- 四种状态：正常、迟到、早退、请假
- 签到/签退时间记录
- 高级查询：按成员、日期范围、状态筛选
- 导出功能：考勤记录导出为 CSV 文件
- 重复检测：同一成员同一天仅能有一条考勤记录

### 4. 统计图表
- 考勤状态分布柱状图
- 各部门考勤记录数对比
- 基于 Matplotlib 实现，界面内嵌显示

### 5. 异常处理
- 数据库断连自动检测（每 60 秒健康检查）
- 输入格式实时校验与友好提示
- 外键约束保护（删除部门/成员时检查关联数据）
- 主键/唯一键冲突明确提示

### 6. 数据库自动初始化
- 首次运行自动创建数据库 `lab_attendance_system` 及四张业务表
- 自动插入示例部门、成员和用户账号

## 技术栈

| 层面 | 技术 |
|------|------|
| 前端 | Tkinter + ttk + Matplotlib |
| 后端 | Python 3.10+ |
| 数据库 | MySQL 8.0+（支持本地服务自动管理） |
| 数据库驱动 | mysql-connector-python（纯 Python 模式） |
| 数据处理 | openpyxl（Excel）、csv（标准库） |
| 打包工具 | PyInstaller（生成独立 exe） |

## 快速开始

### 开发环境运行

```bash
# 1. 克隆项目
git clone https://github.com/mahiro76/LabManageSys.git
cd LabManageSys

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用（自动拉起 MySQL 服务）
python main.py
```

应用启动时自动检测 MySQL 服务状态，若未运行则自动启动。

### 手动管理 MySQL

```bash
# 启动 MySQL
python -c "from mysql_service import start_mysql; start_mysql()"

# 停止 MySQL
python -c "from mysql_service import stop_mysql; stop_mysql()"

# 查看状态
python -c "from mysql_service import print_status; print_status()"

# 交互式守护进程
python mysql_daemon.py
```

### 默认登录账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `123456` |
| 员工 | `staff` | `staff123` |
| 学生 | `student` | `student123` |

## 项目结构

```
LabManageSys/
├── main.py                # 应用入口（轻量 launcher）
├── ui.py                  # UI 表现层（登录 + 5 个功能 Tab 页面）
├── db.py                  # 数据访问层（MySqlManager，封装全部 CRUD）
├── models.py              # 数据模型、常量、验证工具函数
├── config.py              # MySQL 本地服务路径与端口配置
├── mysql_service.py       # MySQL 服务生命周期管理（启动/停止/初始化）
├── mysql_daemon.py        # MySQL 交互式守护进程 CLI
├── LabManageSys.spec      # PyInstaller 打包配置文件
├── check_before_build.py  # 打包前环境检查脚本
├── build.bat              # Windows CMD 一键打包脚本
├── build.ps1              # PowerShell 一键打包脚本
├── requirements.txt       # Python 依赖包列表
└── 示例成员数据.csv        # CSV 批量导入模板
```

## 模块职责与架构

```
main.py
   └── Application (ui.py)
          ├── 启动时调用 _EnsureMySqlRunning() → mysql_service.py
          ├── 登录验证 → db.py / models.py
          ├── 主窗口 → 5 个 Tab 页面
          │      ├── DepartmentPage  (部门管理)
          │      ├── MemberPage      (成员档案)
          │      ├── AttendancePage  (考勤记录)
          │      ├── StatsPage       (统计图表)
          │      └── UserPage        (用户管理)
          └── 数据库健康监控（每 60 秒轮询）
```

| 模块 | 职责 | 关键类/函数 |
|------|------|-------------|
| `main.py` | 程序入口，启动 Application | `main()` |
| `ui.py` | GUI 界面，包含登录窗口和 5 个功能页面 | `class Application`, `class LoginPage`, `class DepartmentPage`, `class MemberPage`, `class AttendancePage`, `class StatsPage`, `class UserPage` |
| `db.py` | 数据访问层，封装所有数据库操作 | `class MySqlManager` — `EnsureSchema()`, `GetMembers()`, `GetAttendanceRecords()`, `AuthenticateUser()`, `UpsertAttendance()`, `ChangePassword()`, `AdminResetPassword()` 等 |
| `models.py` | 数据模型与常量定义 | `class DatabaseConfig`, `class LoginUser`; 常量 `ROLE_ADMIN/STAFF/STUDENT`; 工具函数 `HashPassword()`, `IsValidPhone()`, `IsValidAge()` |
| `config.py` | MySQL 路径配置 | `MYSQL_HOME`, `NEW_ROOT_PASSWORD`, `get_mysqld_path()`, `get_mysql_path()`, `get_mysqladmin_path()` |
| `mysql_service.py` | 管理 MySQL 进程生命周期 | `start_mysql()`, `stop_mysql()`, `is_mysql_running()`, `initialize_mysql()`, `load_state()` |
| `mysql_daemon.py` | 交互式 CLI 管理工具 | 提示用户选择 `1=启动 / 2=停止 / 3=状态 / 4=退出` |

## 角色权限体系

```
                  ┌─────────────────────────────┐
                  │         管理员 admin         │
                  │  全部模块增删改查 + 用户管理  │
                  │  + 重置密码                  │
                  └──────────┬──────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
  ┌───────▼────────┐                ┌──────────▼──────────┐
  │  普通老师 staff │                │    学生 student      │
  │ 部门/成员增删改查│                │ 仅查看本人信息         │
  │ 考勤仅查看       │                │ 仅查看本人考勤记录    │
  │ 统计图表可查看   │                │                     │
  │ 无用户管理权限   │                │                     │
  └────────────────┘                └─────────────────────┘
```

## 数据库设计

### 表结构

**departments（部门表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| department_id | INT PK AUTO_INCREMENT | 部门编号 |
| department_name | VARCHAR(100) UNIQUE NOT NULL | 部门名称 |
| description | VARCHAR(255) | 描述 |
| created_at | DATETIME | 创建时间 |

**members（成员表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| member_id | VARCHAR(32) PK | 成员编号 |
| name | VARCHAR(50) NOT NULL | 姓名 |
| gender | VARCHAR(10) NOT NULL | 性别 |
| age | INT NOT NULL | 年龄 |
| identity | VARCHAR(50) NOT NULL | 身份（老师/学生等） |
| position | VARCHAR(50) NOT NULL | 职位 |
| join_method | VARCHAR(50) NOT NULL | 加入方式 |
| contact | VARCHAR(20) NOT NULL | 联系方式 |
| department_id | INT FK → departments | 所属部门 |
| note | VARCHAR(255) | 备注 |
| created_at / updated_at | DATETIME | 时间戳 |

**attendance_records（考勤记录表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| attendance_id | INT PK AUTO_INCREMENT | 记录编号 |
| member_id | VARCHAR(32) FK → members | 成员编号 |
| attendance_date | DATE NOT NULL | 考勤日期 |
| status | VARCHAR(10) NOT NULL | 状态（正常/迟到/早退/请假） |
| check_in_time | TIME NULL | 签到时间 |
| check_out_time | TIME NULL | 签退时间 |
| remark | VARCHAR(255) | 备注 |
| UNIQUE(member_id, attendance_date) | | 同成员同天唯一约束 |

**user_accounts（用户账号表）**
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INT PK AUTO_INCREMENT | 用户编号 |
| username | VARCHAR(50) UNIQUE NOT NULL | 登录名 |
| password_hash | VARCHAR(64) NOT NULL | 密码哈希（SHA-256） |
| role | VARCHAR(20) NOT NULL | 角色（admin/staff/student） |
| member_id | VARCHAR(32) UNIQUE FK → members | 关联成员 |
| is_active | TINYINT DEFAULT 1 | 是否启用 |
| created_at / updated_at | DATETIME | 时间戳 |

### E-R 关系

```
departments ──1:N──→ members ──1:N──→ attendance_records
                          │
                          └──1:0..1── user_accounts
```

## 配置说明

### MySQL 路径配置（config.py）

```python
MYSQL_HOME = r"D:\mysql"               # MySQL 安装根目录
NEW_ROOT_PASSWORD = "123456"            # root 密码（默认与 db 连接密码一致）
STATE_FILE = os.path.join(MYSQL_HOME, "mysql_setup_state.json")  # 状态文件
```

### 数据库连接默认值（models.py）

```python
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = "3306"
DEFAULT_DB_USER = "root"
DEFAULT_DB_PASSWORD = "123456"          # 与 NEW_ROOT_PASSWORD 保持一致
DEFAULT_DB_NAME = "lab_attendance_system"
```

### 管理员动态修改

应用启动后管理员可通过 **设置 → 数据库配置** 菜单实时修改数据库连接参数，无需编辑代码文件。

## 打包部署

### 前置要求

- Python 3.8+
- 已安装所有依赖：`pip install -r requirements.txt`
- PyInstaller 已安装（已包含在 `requirements.txt` 中）

### 打包方式

#### 方式一：一键打包脚本（推荐）

Windows CMD：
```bash
build.bat
```

PowerShell：
```powershell
.\build.ps1
```

#### 方式二：手动打包

```bash
pyinstaller LabManageSys.spec
```

打包完成后输出位于：
```
dist\LabManageSys\
├── LabManageSys.exe       # 主程序
└── _internal\             # 依赖文件夹
    ├── mysql\             # MySQL 连接器
    ├── openpyxl\          # Excel 处理库
    ├── matplotlib\        # 图表库
    └── ...
```

**整个文件夹大小约 150-250 MB**（含完整 Python 环境与依赖）。

### 打包前检查

使用内置检查脚本验证环境：

```bash
python check_before_build.py
```

该脚本将检查：Python 版本、依赖包、MySQL 服务状态、项目文件完整性、环境清理。

### 注意事项

1. **MySQL 服务依赖**：打包后的程序仍依赖本地 MySQL 服务，目标机器需安装 MySQL 8.0+
2. **首次启动较慢**：Windows Defender 扫描可能导致首次启动 5-10 秒
3. **杀毒软件误报**：可将程序添加至白名单或使用代码签名证书
4. **打包模式**：当前配置为文件夹模式（`onedir`），如需单文件模式可修改 `LabManageSys.spec` 中 `exclude_binaries=False`

### 打包进阶

- **UPX 压缩**：当前配置已禁用 UPX（避免压缩导致 DLL 损坏），如需启用可在 `LabManageSys.spec` 中将 `upx` 设为 `True`
- **应用图标**：准备 `app.ico`，在 `LabManageSys.spec` 中指定 `icon='app.ico'`
- **排除模块**：可在 `excludes` 中添加不需要的模块以减小打包体积

## 常见问题

### Q: 应用启动时提示"无法连接数据库"？

应用会自动尝试启动 MySQL。如果失败，请检查：
1. MySQL 安装路径是否正确（在 `config.py` 中配置 `MYSQL_HOME`）
2. 是否有权限启动 MySQL 服务
3. 端口 3306 是否被占用

手动启动 MySQL：
```bash
python -c "from mysql_service import start_mysql; start_mysql()"
```

### Q: 如何修改 MySQL 安装路径？

编辑 `config.py` 中的 `MYSQL_HOME` 变量：
```python
MYSQL_HOME = r"D:\mysql"    # Windows
MYSQL_HOME = "/opt/mysql"   # Linux/Mac
```

### Q: 如何重置 root 密码？

编辑 `config.py` 中的 `NEW_ROOT_PASSWORD`，然后重新初始化：
```bash
python -c "from mysql_service import initialize_mysql; initialize_mysql(force=True)"
```

### Q: 打包后运行闪退？

使用控制台模式打包以查看错误信息：
```bash
pyinstaller --console LabManageSys.spec
```

### Q: CSV 导入乱码？

确保 CSV 文件使用 UTF-8 with BOM 编码（UTF-8-SIG）。

### Q: Excel 导入失败？

确保 Excel 列顺序为：member_id, name, gender, age, identity, position, join_method, contact, note。

---

**版本**：1.0  
**最后更新**：2026-06-15  
**许可证**：MIT
