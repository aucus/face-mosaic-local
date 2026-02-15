#!/usr/bin/env python3
"""
Windows 앱 빌드 스크립트

PyInstaller를 사용하여 Windows .exe 실행 파일을 생성합니다.
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


def create_icon():
    """Windows용 .ico 아이콘 생성 (없는 경우)"""
    assets_dir = Path('assets')
    assets_dir.mkdir(exist_ok=True)
    
    icon_path = assets_dir / 'icon.ico'
    
    if icon_path.exists():
        print(f"✓ 아이콘 파일 존재: {icon_path}")
        return True
    
    # PNG 아이콘 확인
    icon_png = assets_dir / 'icon.png'
    
    if icon_png.exists():
        print(f"PNG 아이콘을 ICO로 변환 중: {icon_png} → {icon_path}")
        try:
            from PIL import Image
            
            # PNG 로드
            img = Image.open(icon_png)
            
            # ICO 파일로 저장 (다양한 크기 포함)
            # Windows ICO는 여러 크기를 포함할 수 있음
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # 원본 이미지 크기 조정
            if img.size[0] < 256:
                # 작은 이미지는 256x256으로 확대
                img = img.resize((256, 256), Image.Resampling.LANCZOS)
            
            # ICO 파일로 저장 (Pillow가 자동으로 여러 크기 생성)
            img.save(icon_path, format='ICO', sizes=sizes)
            print(f"✓ ICO 아이콘 생성됨: {icon_path}")
            return True
        except Exception as e:
            print(f"⚠ ICO 변환 실패: {e}")
            print("  아이콘 없이 계속 진행합니다...")
            return False
    
    # 기본 아이콘 생성
    print("⚠ 아이콘 파일이 없습니다. 기본 아이콘을 생성합니다...")
    try:
        from PIL import Image, ImageDraw
        
        # 256x256 아이콘 생성
        img = Image.new('RGB', (256, 256), color='#4A90E2')
        draw = ImageDraw.Draw(img)
        
        # 간단한 로고 그리기
        # 외곽 원
        draw.ellipse([20, 20, 236, 236], fill='white', outline='#2C5F8D', width=4)
        # 얼굴 모양
        draw.ellipse([60, 60, 196, 196], fill='#2C5F8D')
        # 모자이크 효과 (사각형들)
        for i in range(5):
            for j in range(5):
                x1 = 70 + i * 12
                y1 = 70 + j * 12
                x2 = x1 + 10
                y2 = y1 + 10
                draw.rectangle([x1, y1, x2, y2], fill='#1A3F5F', outline='#0F2A3F', width=1)
        
        # PNG로 먼저 저장
        img.save(icon_png)
        print(f"✓ 기본 PNG 아이콘 생성: {icon_png}")
        
        # ICO로 변환
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(icon_path, format='ICO', sizes=sizes)
        print(f"✓ 기본 ICO 아이콘 생성: {icon_path}")
        return True
    except Exception as e:
        print(f"⚠ 아이콘 생성 실패: {e}")
        print("  아이콘 없이 계속 진행합니다...")
        return False


def build_windows_exe():
    """Windows 실행 파일 빌드"""
    print("\nWindows 실행 파일 빌드 시작...")
    
    # 아이콘 경로 확인 및 추가
    icon_path = Path('assets/icon.ico')
    icon_args = []
    if icon_path.exists():
        icon_args = ['--icon', str(icon_path)]
        print(f"✓ 아이콘 사용: {icon_path}")
    else:
        print("⚠ 아이콘 파일이 없습니다. 기본 아이콘으로 진행합니다.")
    
    # PyInstaller 실행
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
    ] + icon_args + [
        'pyinstaller_windows.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 빌드 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 빌드 실패:")
        print(e.stderr)
        return False


def verify_icon_applied() -> None:
    """(옵션) 빌드 후 아이콘 사용 여부 검증."""
    exe_path = Path("dist/FaceMosaicLocal.exe")
    icon_path = Path("assets/icon.ico")
    if exe_path.exists() and not icon_path.exists():
        print("⚠ assets/icon.ico 없음 — 기본 아이콘으로 빌드되었을 수 있음")
    elif exe_path.exists() and icon_path.exists():
        print("✓ 아이콘 파일 사용됨: assets/icon.ico")


def verify_exe():
    """실행 파일 검증"""
    print("\n실행 파일 검증 중...")
    
    exe_path = Path('dist/FaceMosaicLocal.exe')
    
    if exe_path.exists():
        # 실행 파일 크기 확인
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ 실행 파일 생성됨: {exe_path} ({size_mb:.1f} MB)")
        
        # 파일 속성 확인
        if exe_path.is_file():
            print("✓ 파일 형식 확인됨")
        else:
            print("⚠ 파일 형식이 올바르지 않습니다")
        
        return True
    else:
        print(f"✗ 실행 파일을 찾을 수 없습니다: {exe_path}")
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
    zip_name = f"FaceMosaicLocal-Pro-v{version}-windows.zip"
    zip_path = Path("dist") / zip_name
    exe_path = Path("dist/FaceMosaicLocal.exe")
    install_guide = Path("docs/INSTALL_GUIDE.md")

    if not exe_path.exists():
        print("✗ 실행 파일을 찾을 수 없어 zip을 생성하지 않습니다.")
        return False
    if not install_guide.exists():
        print("⚠ docs/INSTALL_GUIDE.md가 없습니다. 가이드 없이 zip을 생성합니다.")

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # dist 내 모든 파일 추가 (exe 및 의존 파일, zip 자체 제외)
            for f in Path("dist").rglob("*"):
                if f.is_file() and f != zip_path.resolve():
                    arcname = f.relative_to(Path("dist"))
                    zf.write(f, arcname)
            if install_guide.exists():
                zf.write(install_guide, "INSTALL_GUIDE.md")
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"✓ ZIP 생성됨: {zip_path} ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"✗ ZIP 생성 실패: {e}")
        return False


def main():
    """메인 함수"""
    print("=" * 50)
    print("Face Mosaic Local - Windows 앱 빌드 스크립트")
    print("=" * 50)
    
    # Windows 확인
    if sys.platform != 'win32':
        print("⚠ 경고: 이 스크립트는 Windows에서만 실행할 수 있습니다.")
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
    
    # 실행 파일 빌드
    if not build_windows_exe():
        sys.exit(1)
    
    # 실행 파일 검증
    if not verify_exe():
        sys.exit(1)
    
    # (옵션) 아이콘 적용 여부 검증
    verify_icon_applied()
    
    # ZIP 생성 (빌드 결과물 + INSTALL_GUIDE.md)
    create_release_zip()
    
    print("\n" + "=" * 50)
    print("빌드 완료!")
    print("=" * 50)
    print("\n생성된 파일:")
    print("  dist/FaceMosaicLocal.exe")
    zip_name = f"FaceMosaicLocal-Pro-v{get_version()}-windows.zip"
    if (Path("dist") / zip_name).exists():
        print(f"  dist/{zip_name}")
    print("\n실행 파일 사용 방법:")
    print("  dist/FaceMosaicLocal.exe를 더블클릭하여 실행하거나")
    print("  다른 컴퓨터로 복사하여 바로 실행할 수 있습니다.")


if __name__ == '__main__':
    main()
