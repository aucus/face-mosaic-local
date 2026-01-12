# -*- mode: python ; coding: utf-8 -*-
# macOS 앱 빌드를 위한 PyInstaller 설정 파일

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
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
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
    icon=None,  # 아이콘은 build_macos.py에서 처리
)

app = BUNDLE(
    exe,
    name='FaceMosaicLocal.app',
    icon=None,  # 아이콘은 build_macos.py에서 처리
    bundle_identifier='com.facemosaic.local',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'Face Mosaic Local',
        'CFBundleDisplayName': 'Face Mosaic Local',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2026',
        'NSPhotoLibraryUsageDescription': '이 앱은 이미지 파일에 접근하여 얼굴 모자이크 처리를 수행합니다.',
        'NSDocumentsFolderUsageDescription': '이 앱은 이미지 파일을 읽고 저장하기 위해 문서 폴더에 접근합니다.',
    },
)
