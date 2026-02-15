#!/usr/bin/env python3
"""
macOS 앱 빌드 스크립트

PyInstaller를 사용하여 macOS .app 번들을 생성합니다.
빌드 완료 후 dist/를 zip으로 압축하며 INSTALL_GUIDE.md를 포함합니다.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path


def clean_build_dirs():
    """빌드 디렉토리 정리"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"정리 중: {dir_name}/")
            shutil.rmtree(dir_path)
    
    # .spec 파일로 생성된 임시 파일 정리
    for spec_file in Path('.').glob('*.spec'):
        if spec_file.name not in ['pyinstaller.spec', 'pyinstaller_macos.spec', 'pyinstaller_windows.spec']:
            print(f"삭제 중: {spec_file}")
            spec_file.unlink()


def check_dependencies():
    """필수 의존성 확인"""
    print("의존성 확인 중...")
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller 설치됨: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller가 설치되지 않았습니다.")
        print("  설치: pip install pyinstaller")
        return False
    
    # 모델 파일 확인
    model_files = [
        'models/deploy.prototxt',
        'models/res10_300x300_ssd_iter_140000.caffemodel'
    ]
    
    missing_files = []
    for file_path in model_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠ 경고: 다음 모델 파일이 없습니다: {', '.join(missing_files)}")
        print("  다운로드: python download_models.py")
    else:
        print("✓ 모델 파일 확인됨")
    
    return True


def verify_icon_applied() -> None:
    """(옵션) 빌드 후 아이콘이 적용되었는지 검증."""
    app_path = Path("dist/FaceMosaicLocal.app")
    if not app_path.exists():
        return
    # macOS .app 아이콘: Contents/Resources/*.icns 또는 AppIcon.icns
    resources = app_path / "Contents" / "Resources"
    if resources.exists():
        icns = list(resources.glob("*.icns"))
        if icns:
            print(f"✓ 앱 번들 내 아이콘 확인: {icns[0].name}")
        else:
            print("⚠ 앱 번들에 .icns 아이콘 없음 (assets/icon.icns 또는 icon.png 확인)")


def create_icon():
    """기본 아이콘 생성 (없는 경우)"""
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    icon_path = assets_dir / 'icon.icns'
    
    if icon_path.exists():
        print(f"✓ 아이콘 파일 존재: {icon_path}")
        return True
    
    # PNG 아이콘 생성 (나중에 .icns로 변환 가능)
    icon_png = assets_dir / 'icon.png'
    
    if not icon_png.exists():
        print("⚠ 아이콘 파일이 없습니다. 기본 아이콘을 생성합니다...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 1024x1024 아이콘 생성
            img = Image.new('RGB', (1024, 1024), color='#4A90E2')
            draw = ImageDraw.Draw(img)
            
            # 간단한 로고 그리기
            # 외곽 원
            draw.ellipse([100, 100, 924, 924], fill='white', outline='#2C5F8D', width=20)
            # 얼굴 모양
            draw.ellipse([300, 300, 724, 724], fill='#2C5F8D')
            # 모자이크 효과 (사각형들)
            for i in range(5):
                for j in range(5):
                    x1 = 350 + i * 50
                    y1 = 350 + j * 50
                    x2 = x1 + 40
                    y2 = y1 + 40
                    draw.rectangle([x1, y1, x2, y2], fill='#1A3F5F', outline='#0F2A3F', width=2)
            
            img.save(icon_png)
            print(f"✓ 기본 아이콘 생성: {icon_png}")
            print("  참고: .icns 파일로 변환하려면 'iconutil' 명령어를 사용하세요:")
            print(f"    mkdir icon.iconset")
            print(f"    sips -z 16 16 {icon_png} --out icon.iconset/icon_16x16.png")
            print(f"    sips -z 32 32 {icon_png} --out icon.iconset/icon_16x16@2x.png")
            print(f"    # ... (다양한 크기)")
            print(f"    iconutil -c icns icon.iconset -o {icon_path}")
        except Exception as e:
            print(f"⚠ 아이콘 생성 실패: {e}")
            print("  아이콘 없이 계속 진행합니다...")
            return False
    
    return True


def build_macos_app():
    """macOS 앱 빌드"""
    print("\nmacOS 앱 빌드 시작...")
    
    # 아이콘 경로 확인 및 추가
    icon_path = Path('assets/icon.icns')
    icon_args = []
    if icon_path.exists():
        icon_args = ['--icon', str(icon_path)]
        print(f"✓ 아이콘 사용: {icon_path}")
    
    # PyInstaller 실행
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
    ] + icon_args + [
        'pyinstaller_macos.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 빌드 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 빌드 실패:")
        print(e.stderr)
        return False


def verify_app():
    """앱 번들 검증"""
    print("\n앱 번들 검증 중...")
    
    app_path = Path('dist/FaceMosaicLocal.app')
    
    if app_path.exists():
        # 앱 크기 확인
        size_mb = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file()) / (1024 * 1024)
        print(f"✓ 앱 번들 생성됨: {app_path} ({size_mb:.1f} MB)")
        
        # Info.plist 확인
        info_plist = app_path / 'Contents' / 'Info.plist'
        if info_plist.exists():
            print("✓ Info.plist 확인됨")
        else:
            print("⚠ Info.plist를 찾을 수 없습니다")
        
        # 실행 파일 확인
        macos_dir = app_path / 'Contents' / 'MacOS'
        if macos_dir.exists():
            exe_files = list(macos_dir.glob('*'))
            if exe_files:
                print(f"✓ 실행 파일 확인됨: {exe_files[0].name}")
            else:
                print("⚠ 실행 파일을 찾을 수 없습니다")
        
        return True
    else:
        print(f"✗ 앱 번들을 찾을 수 없습니다: {app_path}")
        return False


def get_version() -> str:
    """프로젝트 버전 반환 (src.__version__)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from src import __version__
        return __version__
    except Exception:
        return "0.1.0"


def create_release_zip() -> bool:
    """빌드 결과물을 zip으로 압축 (INSTALL_GUIDE.md 포함)."""
    version = get_version()
    zip_name = f"FaceMosaicLocal-Pro-v{version}-macos.zip"
    zip_path = Path("dist") / zip_name
    app_path = Path("dist/FaceMosaicLocal.app")
    install_guide = Path("docs/INSTALL_GUIDE.md")

    if not app_path.exists():
        print("✗ 앱 번들을 찾을 수 없어 zip을 생성하지 않습니다.")
        return False
    if not install_guide.exists():
        print("⚠ docs/INSTALL_GUIDE.md가 없습니다. 가이드 없이 zip을 생성합니다.")

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # 앱 번들 전체 추가
            for f in app_path.rglob("*"):
                if f.is_file():
                    arcname = f.relative_to(Path("dist"))
                    zf.write(f, arcname)
            # 설치 가이드 추가
            if install_guide.exists():
                zf.write(install_guide, "INSTALL_GUIDE.md")
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"✓ ZIP 생성됨: {zip_path} ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"✗ ZIP 생성 실패: {e}")
        return False


def create_dmg():
    """DMG 파일 생성 (선택)"""
    print("\nDMG 생성 중...")
    
    app_path = Path('dist/FaceMosaicLocal.app')
    dmg_path = Path('dist/FaceMosaicLocal.dmg')
    
    if not app_path.exists():
        print("✗ 앱 번들을 찾을 수 없습니다")
        return False
    
    try:
        # hdiutil을 사용하여 DMG 생성
        cmd = [
            'hdiutil', 'create',
            '-volname', 'Face Mosaic Local',
            '-srcfolder', str(app_path),
            '-ov',
            '-format', 'UDZO',
            str(dmg_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if dmg_path.exists():
            size_mb = dmg_path.stat().st_size / (1024 * 1024)
            print(f"✓ DMG 생성됨: {dmg_path} ({size_mb:.1f} MB)")
            return True
        else:
            print("✗ DMG 생성 실패")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"✗ DMG 생성 실패: {e.stderr}")
        return False
    except FileNotFoundError:
        print("⚠ hdiutil을 찾을 수 없습니다 (macOS 전용)")
        return False


def main():
    """메인 함수"""
    print("=" * 50)
    print("Face Mosaic Local - macOS 앱 빌드 스크립트")
    print("=" * 50)
    
    # macOS 확인
    if sys.platform != 'darwin':
        print("⚠ 경고: 이 스크립트는 macOS에서만 실행할 수 있습니다.")
        response = input("계속하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 아이콘 생성
    create_icon()
    
    # 빌드 디렉토리 정리
    print("\n빌드 디렉토리 정리 중...")
    clean_build_dirs()
    
    # 앱 빌드
    if not build_macos_app():
        sys.exit(1)
    
    # 앱 검증
    if not verify_app():
        sys.exit(1)
    
    # (옵션) 아이콘 적용 여부 검증
    verify_icon_applied()
    
    # ZIP 생성 (빌드 결과물 + INSTALL_GUIDE.md)
    create_release_zip()

    # DMG 생성 (선택)
    print("\nDMG를 생성하시겠습니까? (y/N): ", end='')
    create_dmg_choice = input().lower()
    if create_dmg_choice == 'y':
        create_dmg()
    
    print("\n" + "=" * 50)
    print("빌드 완료!")
    print("=" * 50)
    print("\n생성된 파일:")
    print("  dist/FaceMosaicLocal.app")
    zip_name = f"FaceMosaicLocal-Pro-v{get_version()}-macos.zip"
    if (Path("dist") / zip_name).exists():
        print(f"  dist/{zip_name}")
    if Path('dist/FaceMosaicLocal.dmg').exists():
        print("  dist/FaceMosaicLocal.dmg")
    print("\n앱 실행 방법:")
    print("  open dist/FaceMosaicLocal.app")


if __name__ == '__main__':
    main()
