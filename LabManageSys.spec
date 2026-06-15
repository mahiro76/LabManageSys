s# -*- mode: python ; coding: utf-8 -*-

"""
实验室考勤管理系统 PyInstaller 打包配置
使用方法：pyinstaller LabManageSys.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 如果需要包含额外的数据文件（如模板、配置文件等），在此添加
        # ('data/*.csv', 'data'),
        # ('示例成员数据.csv', '.'),  # 可选：包含示例CSV文件
    ],
    hiddenimports=[
        # MySQL 连接器及其依赖
        'mysql.connector',
        'mysql.connector.constants',
        'mysql.connector.network',
        'mysql.connector.protocol',
        # Excel 处理库
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        # Matplotlib 及其后端
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.pyplot',
        'numpy',  # matplotlib 依赖
        # Tkinter 组件
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        # 其他可能需要的模块
        'csv',
        'datetime',
        'hashlib',
        're',
        'subprocess',
        'json',
        'os',
        'sys',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的测试和开发模块以减小体积
        'pytest',
        'pdb',
        'idlelib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LabManageSys',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用 UPX，避免压缩导致 DLL 损坏
    console=True,  # 显示控制台窗口（调试用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件，可以指定路径，例如: icon='app.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 禁用 UPX，避免压缩导致 DLL 损坏
    upx_exclude=[],
    name='LabManageSys',
)
