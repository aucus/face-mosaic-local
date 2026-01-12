#!/usr/bin/env python3
"""
단일 실행 파일 빌드 스크립트

PyInstaller를 사용하여 모든 의존성을 포함한 단일 실행 파일을 생성합니다.
"""

import os
import sys
import shutil
import subprocess
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
        if spec_file.name != 'pyinstaller.spec':
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


def build_executable():
    """실행 파일 빌드"""
    print("\n빌드 시작...")
    
    # PyInstaller 실행
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'pyinstaller.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 빌드 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 빌드 실패:")
        print(e.stderr)
        return False


def verify_build():
    """빌드 결과 검증"""
    print("\n빌드 결과 검증 중...")
    
    # 플랫폼별 실행 파일 확인
    if sys.platform == 'win32':
        exe_path = Path('dist/face-mosaic-local.exe')
    elif sys.platform == 'darwin':
        exe_path = Path('dist/face-mosaic-local.app/Contents/MacOS/face-mosaic-local')
    else:
        exe_path = Path('dist/face-mosaic-local')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ 실행 파일 생성됨: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"✗ 실행 파일을 찾을 수 없습니다: {exe_path}")
        return False


def main():
    """메인 함수"""
    print("=" * 50)
    print("Face Mosaic Local - 빌드 스크립트")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 빌드 디렉토리 정리
    print("\n빌드 디렉토리 정리 중...")
    clean_build_dirs()
    
    # 빌드 실행
    if not build_executable():
        sys.exit(1)
    
    # 빌드 결과 검증
    if not verify_build():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("빌드 완료!")
    print("=" * 50)
    print("\n실행 파일 위치:")
    if sys.platform == 'win32':
        print("  dist/face-mosaic-local.exe")
    elif sys.platform == 'darwin':
        print("  dist/face-mosaic-local.app")
    else:
        print("  dist/face-mosaic-local")


if __name__ == '__main__':
    main()
