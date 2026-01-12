#!/usr/bin/env python3
"""
DNN 모델 파일 다운로드 스크립트

OpenCV DNN 얼굴 감지에 필요한 모델 파일을 다운로드합니다.
"""

import os
import urllib.request
from pathlib import Path

# 모델 파일 URL (OpenCV 공식 샘플)
MODEL_URLS = {
    "deploy.prototxt": "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    "res10_300x300_ssd_iter_140000.caffemodel": "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
}

MODELS_DIR = Path(__file__).parent / "models"


def download_file(url: str, dest_path: Path) -> bool:
    """
    파일을 다운로드합니다.
    
    Args:
        url: 다운로드 URL
        dest_path: 저장 경로
    
    Returns:
        성공 여부
    """
    try:
        print(f"다운로드 중: {dest_path.name}...")
        urllib.request.urlretrieve(url, dest_path)
        print(f"✓ 완료: {dest_path.name}")
        return True
    except Exception as e:
        print(f"✗ 실패: {dest_path.name} - {e}")
        return False


def main():
    """모델 파일 다운로드 메인 함수"""
    # models 디렉토리 생성
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("DNN 모델 파일 다운로드를 시작합니다...\n")
    
    success_count = 0
    for filename, url in MODEL_URLS.items():
        dest_path = MODELS_DIR / filename
        
        # 이미 존재하면 스킵
        if dest_path.exists():
            print(f"⊙ 이미 존재: {filename} (스킵)")
            success_count += 1
            continue
        
        if download_file(url, dest_path):
            success_count += 1
    
    print(f"\n완료: {success_count}/{len(MODEL_URLS)} 파일 다운로드됨")
    
    if success_count == len(MODEL_URLS):
        print("\n모든 모델 파일이 준비되었습니다!")
    else:
        print("\n일부 파일 다운로드에 실패했습니다. 수동으로 다운로드해주세요.")


if __name__ == "__main__":
    main()
