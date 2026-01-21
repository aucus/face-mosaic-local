# -*- mode: python ; coding: utf-8 -*-
# Windows 앱 빌드를 위한 PyInstaller 설정 파일

block_cipher = None

a = Analysis(
    ['gui/main_window.py'],  # GUI 진입점 사용
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),  # DNN 모델 파일 포함
        ('logo', 'logo'),      # 로고 파일 포함 (선택)
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL',
        'tqdm',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FaceMosaicLocal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 모드 (콘솔 창 없음)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘은 build_windows.py에서 처리
)
