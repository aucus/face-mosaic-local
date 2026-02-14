"""
유틸리티 함수 모듈

파일 처리, 이미지 I/O, 로깅 설정 등의 유틸리티 함수를 제공합니다.
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageOps


# 지원하는 이미지 확장자
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def get_image_files(folder: str, recursive: bool = False) -> List[Path]:
    """
    폴더에서 이미지 파일 목록을 가져옵니다.
    
    Args:
        folder: 검색할 폴더 경로
        recursive: 하위 폴더까지 재귀적으로 검색할지 여부
    
    Returns:
        이미지 파일 경로 리스트
    """
    folder_path = Path(folder)
    
    if not folder_path.exists():
        raise FileNotFoundError(f"폴더를 찾을 수 없습니다: {folder}")
    
    if not folder_path.is_dir():
        raise ValueError(f"폴더가 아닙니다: {folder}")
    
    image_files = []
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for file_path in folder_path.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
            image_files.append(file_path)
    
    return sorted(image_files)


def load_image(path: str) -> Tuple[np.ndarray, Optional[bytes]]:
    """
    이미지 파일을 로드하고 EXIF 메타데이터를 보존합니다.
    
    Args:
        path: 이미지 파일 경로
    
    Returns:
        (이미지 배열 (BGR), EXIF raw bytes) 튜플
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")
    
    # Pillow로 로드
    pil_image = Image.open(path)
    
    # EXIF raw bytes 보존 (저장 시 그대로 전달하기 위함)
    exif_bytes = pil_image.info.get("exif", None)
    
    # EXIF Orientation 적용 (세로 사진 등 회전 정보 반영)
    pil_image = ImageOps.exif_transpose(pil_image)
    
    # OpenCV 형식으로 변환 (BGR)
    image_array = np.array(pil_image)
    
    # RGB → BGR 변환
    if len(image_array.shape) == 3:
        if image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        elif image_array.shape[2] == 4:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGRA)
    
    return image_array, exif_bytes


def save_image(
    image: np.ndarray,
    path: str,
    quality: int = 95,
    exif_data: Optional[bytes] = None
) -> None:
    """
    이미지를 저장하고 EXIF 메타데이터를 보존합니다.
    
    Args:
        image: 저장할 이미지 (BGR 형식)
        path: 저장 경로
        quality: JPEG 품질 (1-100, 기본값: 95)
        exif_data: EXIF raw bytes (load_image()에서 받은 값)
    """
    path_obj = Path(path)
    
    # 출력 디렉토리 생성
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # BGR → RGB 변환
    if len(image.shape) == 3:
        if image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif image.shape[2] == 4:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        else:
            image_rgb = image
    else:
        image_rgb = image
    
    # PIL Image로 변환
    pil_image = Image.fromarray(image_rgb)
    
    # 저장
    is_jpeg = path_obj.suffix.lower() in {".jpg", ".jpeg"}
    
    if is_jpeg:
        save_kwargs = {"quality": quality}
        # EXIF raw bytes가 있으면 그대로 전달
        if exif_data and isinstance(exif_data, bytes):
            save_kwargs["exif"] = exif_data
        pil_image.save(path, **save_kwargs)
    else:
        pil_image.save(path)


def setup_logger(
    name: str = "face_mosaic",
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    로거를 설정합니다 (파일 + 콘솔 핸들러).
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로 (None이면 파일 핸들러 미사용)
        level: 로그 레벨
    
    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()
    
    # 로그 포맷
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (지정된 경우)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
