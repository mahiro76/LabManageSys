"""业务数据访问层 (MySqlManager)。

封装 MySQL 数据库的连接管理、表结构初始化、以及业务 CRUD 操作。
"""

from typing import Any, Dict, List, Optional, Tuple

import mysql.connector

from models import DatabaseConfig, HashPassword


class MySqlManager:
    """MySQL 数据访问层。

    负责：
    1. 建立数据库连接
    2. 初始化数据库表结构
    3. 提供常用增删改查方法
    4. 在连接失效时给出明确提示
    """

    def __init__(self, Config: DatabaseConfig) -> None:
        self.Config = Config
        self.Connection: Optional[mysql.connector.MySQLConnection] = None

    def Close(self) -> None:
        """关闭数据库连接。"""
        if self.Connection is not None and self.Connection.is_connected():
            self.Connection.close()
        self.Connection = None

    def EnsureConnection(self) -> None:
        """确保连接处于可用状态。"""
        if self.Connection is not None and self.Connection.is_connected():
            return
        try:
            self.Connection = mysql.connector.connect(
                host=self.Config.Host,
                port=self.Config.Port,
                user=self.Config.User,
                password=self.Config.Password,
                database=self.Config.Database,
                charset="utf8mb4",
                autocommit=True,
                connect_timeout=5,
                use_pure=True,  # 使用纯 Python 实现，避免 C 扩展崩溃 (0xC0000005)
            ) # type: ignore
        except mysql.connector.Error:
            raise
        except Exception as e:
            raise mysql.connector.Error(
                f"连接数据库时发生未知错误: {e}"
            ) from e

    def _ConnectWithoutDatabase(self) -> mysql.connector.MySQLConnection:
        """建立不指定数据库的连接，用于创建数据库。"""
        try:
            return mysql.connector.connect(
                host=self.Config.Host,
                port=self.Config.Port,
                user=self.Config.User,
                password=self.Config.Password,
                charset="utf8mb4",
                autocommit=True,
                connect_timeout=5,
                use_pure=True,  # 使用纯 Python 实现，避免 C 扩展崩溃 (0xC0000005)
            ) # type: ignore
        except mysql.connector.Error:
            raise
        except Exception as e:
            raise mysql.connector.Error(
                f"连接数据库时发生未知错误: {e}"
            ) from e

    # ---- 数据库与表结构初始化 ----

    def EnsureSchema(self) -> None:
        """创建数据库与表结构，并写入默认示例数据。"""
        RootConnection = self._ConnectWithoutDatabase()
        RootCursor = RootConnection.cursor()
        try:
            RootCursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.Config.Database}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
            )
        finally:
            RootCursor.close()
            RootConnection.close()

        self.Close()
        self.EnsureConnection()
        Cursor = self.Connection.cursor()
        try:
            self._CreateTables(Cursor)
            self._SeedDemoData(Cursor)
        finally:
            Cursor.close()

    def _CreateTables(self, Cursor: mysql.connector.cursor.MySQLCursor) -> None:
        """创建四张业务表。"""
        Cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT PRIMARY KEY AUTO_INCREMENT,
                department_name VARCHAR(100) NOT NULL UNIQUE,
                description VARCHAR(255) DEFAULT '',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        Cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                member_id VARCHAR(32) PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                age INT NOT NULL,
                identity VARCHAR(50) NOT NULL,
                position VARCHAR(50) NOT NULL,
                join_method VARCHAR(50) NOT NULL,
                contact VARCHAR(20) NOT NULL,
                department_id INT NULL,
                note VARCHAR(255) DEFAULT '',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT FK_Members_Department
                    FOREIGN KEY (department_id) REFERENCES departments(department_id)
                    ON UPDATE CASCADE ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        Cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance_records (
                attendance_id INT PRIMARY KEY AUTO_INCREMENT,
                member_id VARCHAR(32) NOT NULL,
                attendance_date DATE NOT NULL,
                status VARCHAR(10) NOT NULL,
                check_in_time TIME NULL,
                check_out_time TIME NULL,
                remark VARCHAR(255) DEFAULT '',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY UkMemberDate (member_id, attendance_date),
                CONSTRAINT FK_Attendance_Member
                    FOREIGN KEY (member_id) REFERENCES members(member_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        Cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_accounts (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(64) NOT NULL,
                role VARCHAR(20) NOT NULL,
                member_id VARCHAR(32) NULL UNIQUE,
                is_active TINYINT NOT NULL DEFAULT 1,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT FK_Users_Member
                    FOREIGN KEY (member_id) REFERENCES members(member_id)
                    ON UPDATE CASCADE ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

    def _SeedDemoData(self, Cursor: mysql.connector.cursor.MySQLCursor) -> None:
        """当系统为空时，写入默认示例数据，便于首次演示和测试。"""
        # 使用 dictionary cursor 以便按列名访问
        DictCursor = self.Connection.cursor(dictionary=True)
        try:
            DictCursor.execute("SELECT COUNT(*) AS TotalCount FROM departments")
            DepartmentCount = DictCursor.fetchone()["TotalCount"]
            if DepartmentCount == 0:
                Cursor.execute(
                    """
                    INSERT INTO departments (department_name, description)
                    VALUES
                    ('综合管理组', '负责实验室系统与日常协调'),
                    ('实验教学组', '负责教学实验与指导'),
                    ('学生实验组', '负责学生实验与考勤')
                    """
                )

            DictCursor.execute("SELECT COUNT(*) AS TotalCount FROM members")
            MemberCount = DictCursor.fetchone()["TotalCount"]
            if MemberCount == 0:
                DictCursor.execute(
                    "SELECT department_id FROM departments ORDER BY department_id ASC LIMIT 1"
                )
                FirstDepartment = DictCursor.fetchone()
                DictCursor.execute(
                    "SELECT department_id FROM departments ORDER BY department_id DESC LIMIT 1"
                )
                LastDepartment = DictCursor.fetchone()
                Cursor.execute(
                    """
                    INSERT INTO members
                    (member_id, name, gender, age, identity, position, join_method, contact, department_id, note)
                    VALUES
                    ('T001', '王老师', '男', 35, '老师', '实验室负责人', '聘任', '13800000001', %s, '系统示例老师'),
                    ('S001', '李同学', '女', 22, '学生', '研究生', '招收', '13800000002', %s, '系统示例学生')
                    """,
                    (FirstDepartment["department_id"], LastDepartment["department_id"]),
                )

            DictCursor.execute("SELECT COUNT(*) AS TotalCount FROM user_accounts")
            AccountCount = DictCursor.fetchone()["TotalCount"]
            if AccountCount == 0:
                Cursor.execute(
                    """
                    INSERT INTO user_accounts
                    (username, password_hash, role, member_id, is_active)
                    VALUES
                    ('admin', %s, 'admin', NULL, 1),
                    ('staff', %s, 'staff', 'T001', 1),
                    ('student', %s, 'student', 'S001', 1)
                    """,
                    (
                        HashPassword("123456"),
                        HashPassword("staff123"),
                        HashPassword("student123"),
                    ),
                )
        finally:
            DictCursor.close()

    # ---- 通用查询方法 ----

    def ExecuteQuery(self, SqlText: str, Parameters: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """执行查询语句并返回字典列表。"""
        self.EnsureConnection()
        Cursor = self.Connection.cursor(dictionary=True)
        try:
            Cursor.execute(SqlText, Parameters)
            return Cursor.fetchall()
        finally:
            Cursor.close()

    def ExecuteOne(self, SqlText: str, Parameters: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        """执行查询语句并返回首条结果。"""
        Rows = self.ExecuteQuery(SqlText, Parameters)
        return Rows[0] if Rows else None

    def ExecuteNonQuery(self, SqlText: str, Parameters: Tuple[Any, ...] = ()) -> int:
        """执行增删改语句并返回影响行数。"""
        self.EnsureConnection()
        Cursor = self.Connection.cursor()
        try:
            Cursor.execute(SqlText, Parameters)
            return Cursor.rowcount
        finally:
            Cursor.close()

    # ---- 部门管理 ----

    def GetDepartments(self) -> List[Dict[str, Any]]:
        """查询全部部门。"""
        return self.ExecuteQuery(
            "SELECT department_id, department_name, description FROM departments ORDER BY department_id ASC"
        )

    def UpsertDepartment(self, DepartmentId: Optional[int], DepartmentName: str, Description: str) -> None:
        """新增或修改部门。"""
        if DepartmentId is None:
            self.ExecuteNonQuery(
                """
                INSERT INTO departments (department_name, description)
                VALUES (%s, %s)
                """,
                (DepartmentName, Description),
            )
            return
        self.ExecuteNonQuery(
            """
            UPDATE departments
            SET department_name = %s, description = %s
            WHERE department_id = %s
            """,
            (DepartmentName, Description, DepartmentId),
        )

    def DeleteDepartment(self, DepartmentId: int) -> None:
        """删除部门。若部门下存在成员，成员的部门会自动置空。"""
        self.ExecuteNonQuery("DELETE FROM departments WHERE department_id = %s", (DepartmentId,))

    # ---- 成员管理 ----

    def GetMembers(
        self,
        Keyword: str = "",
        DepartmentId: Optional[int] = None,
        MemberId: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """查询成员档案。"""
        SqlText = """
            SELECT m.member_id, m.name, m.gender, m.age, m.identity, m.position,
                   m.join_method, m.contact, m.department_id, m.note,
                   IFNULL(d.department_name, '') AS department_name
            FROM members m
            LEFT JOIN departments d ON m.department_id = d.department_id
            WHERE 1 = 1
        """
        Parameters: List[Any] = []
        if Keyword:
            SqlText += """
                AND (
                    m.member_id LIKE %s OR m.name LIKE %s
                )
            """
            LikeValue = f"%{Keyword}%"
            Parameters.extend([LikeValue, LikeValue])
        if DepartmentId is not None:
            SqlText += " AND m.department_id = %s"
            Parameters.append(DepartmentId)
        if MemberId:
            SqlText += " AND m.member_id = %s"
            Parameters.append(MemberId)
        SqlText += " ORDER BY m.member_id ASC"
        return self.ExecuteQuery(SqlText, tuple(Parameters))

    # ---- 考勤记录管理 ----

    def GetAttendanceRecords(
        self,
        MemberId: Optional[str] = None,
        StartDate: str = "",
        EndDate: str = "",
        Status: str = "",
    ) -> List[Dict[str, Any]]:
        """查询考勤记录。"""
        SqlText = """
            SELECT a.attendance_id, a.member_id, a.attendance_date, a.status,
                   a.check_in_time, a.check_out_time, a.remark,
                   m.name AS member_name, m.department_id,
                   IFNULL(d.department_name, '') AS department_name
            FROM attendance_records a
            JOIN members m ON a.member_id = m.member_id
            LEFT JOIN departments d ON m.department_id = d.department_id
            WHERE 1 = 1
        """
        Parameters: List[Any] = []
        if MemberId:
            SqlText += " AND a.member_id LIKE %s"
            Parameters.append(f"%{MemberId}%")
        if StartDate:
            SqlText += " AND a.attendance_date >= %s"
            Parameters.append(StartDate)
        if EndDate:
            SqlText += " AND a.attendance_date <= %s"
            Parameters.append(EndDate)
        if Status:
            SqlText += " AND a.status = %s"
            Parameters.append(Status)
        SqlText += " ORDER BY a.attendance_date DESC, a.member_id ASC"
        return self.ExecuteQuery(SqlText, tuple(Parameters))

    def UpsertAttendance(
        self,
        AttendanceId: Optional[int],
        MemberId: str,
        Date: str,
        Status: str,
        CheckIn: Optional[str] = None,
        CheckOut: Optional[str] = None,
        Remark: str = "",
    ) -> None:
        """新增或修改考勤记录。"""
        if AttendanceId is None:
            self.ExecuteNonQuery(
                """
                INSERT INTO attendance_records
                (member_id, attendance_date, status, check_in_time, check_out_time, remark)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (MemberId, Date, Status, CheckIn, CheckOut, Remark),
            )
        else:
            self.ExecuteNonQuery(
                """
                UPDATE attendance_records
                SET member_id = %s, attendance_date = %s, status = %s,
                    check_in_time = %s, check_out_time = %s, remark = %s
                WHERE attendance_id = %s
                """,
                (MemberId, Date, Status, CheckIn, CheckOut, Remark, AttendanceId),
            )

    def DeleteAttendance(self, AttendanceId: int) -> None:
        """删除考勤记录。"""
        self.ExecuteNonQuery("DELETE FROM attendance_records WHERE attendance_id = %s", (AttendanceId,))

    # ---- 用户账户管理 ----

    def GetUsers(self) -> List[Dict[str, Any]]:
        """查询全部用户账户（关联成员姓名）。"""
        return self.ExecuteQuery(
            """
            SELECT u.user_id, u.username, u.role, u.member_id, u.is_active,
                   IFNULL(m.name, '') AS member_name
            FROM user_accounts u
            LEFT JOIN members m ON u.member_id = m.member_id
            ORDER BY u.user_id ASC
            """
        )

    def AuthenticateUser(self, Username: str, Password: str) -> Optional[Dict[str, Any]]:
        """验证用户登录，成功返回用户信息。"""
        return self.ExecuteOne(
            """
            SELECT u.user_id, u.username, u.role, u.member_id,
                   IFNULL(m.name, u.username) AS display_name
            FROM user_accounts u
            LEFT JOIN members m ON u.member_id = m.member_id
            WHERE u.username = %s AND u.password_hash = %s AND u.is_active = 1
            """,
            (Username, HashPassword(Password)),
        )

    def UpsertUser(
        self,
        UserId: Optional[int],
        Username: str,
        Password: str,
        Role: str,
        MemberId: Optional[str] = None,
        IsActive: bool = True,
    ) -> None:
        """新增或修改用户账户。"""
        if UserId is None:
            self.ExecuteNonQuery(
                """
                INSERT INTO user_accounts (username, password_hash, role, member_id, is_active)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (Username, HashPassword(Password), Role, MemberId, int(IsActive)),
            )
        else:
            self.ExecuteNonQuery(
                """
                UPDATE user_accounts
                SET username = %s, role = %s, member_id = %s, is_active = %s
                WHERE user_id = %s
                """,
                (Username, Role, MemberId, int(IsActive), UserId),
            )

    def DeleteUser(self, UserId: int) -> None:
        """删除用户账户。"""
        self.ExecuteNonQuery("DELETE FROM user_accounts WHERE user_id = %s", (UserId,))

    def AdminResetPassword(self, UserId: int, NewPassword: str) -> None:
        """管理员直接重置用户密码（无需旧密码验证）。"""
        self.ExecuteNonQuery(
            "UPDATE user_accounts SET password_hash = %s WHERE user_id = %s",
            (HashPassword(NewPassword), UserId),
        )

    def ChangePassword(self, UserId: int, OldPassword: str, NewPassword: str) -> bool:
        """修改用户密码。验证旧密码正确后更新为新密码，成功返回 True。"""
        self.EnsureConnection()
        Cursor = self.Connection.cursor()
        try:
            # 验证旧密码
            Cursor.execute(
                "SELECT user_id FROM user_accounts WHERE user_id = %s AND password_hash = %s",
                (UserId, HashPassword(OldPassword)),
            )
            if Cursor.fetchone() is None:
                return False
            # 更新为新密码
            Cursor.execute(
                "UPDATE user_accounts SET password_hash = %s WHERE user_id = %s",
                (HashPassword(NewPassword), UserId),
            )
            return True
        finally:
            Cursor.close()
