"""
워터마크/로고 추가 모듈

처리된 이미지에 로고를 추가하는 기능을 제공합니다.
"""

from typing import Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def load_logo(logo_path: str) -> Tuple[np.ndarray, bool]:
    """
    로고 이미지를 로드합니다.
    
    Args:
        logo_path: 로고 파일 경로
    
    Returns:
        (로고 이미지 (BGR 또는 BGRA), 알파 채널 여부) 튜플
    
    Raises:
        FileNotFoundError: 로고 파일이 존재하지 않는 경우
    """
    logo_file = Path(logo_path)
    
    if not logo_file.exists():
        raise FileNotFoundError(f"로고 파일을 찾을 수 없습니다: {logo_path}")
    
    # PIL로 로드 (알파 채널 지원)
    pil_logo = Image.open(logo_path)
    
    # RGBA 또는 RGB로 변환
    if pil_logo.mode == 'RGBA':
        has_alpha = True
        logo_array = np.array(pil_logo)
        # RGBA → BGRA
        logo_bgra = cv2.cvtColor(logo_array, cv2.COLOR_RGBA2BGRA)
        return logo_bgra, has_alpha
    else:
        has_alpha = False
        # RGB로 변환
        if pil_logo.mode != 'RGB':
            pil_logo = pil_logo.convert('RGB')
        logo_array = np.array(pil_logo)
        # RGB → BGR
        logo_bgr = cv2.cvtColor(logo_array, cv2.COLOR_RGB2BGR)
        return logo_bgr, has_alpha


def resize_logo(
    logo: np.ndarray,
    target_size: Optional[Tuple[int, int]] = None,
    scale: Optional[float] = None,
    base_image_size: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """
    로고 크기를 조절합니다.
    
    Args:
        logo: 로고 이미지
        target_size: 목표 크기 (width, height), None이면 scale 사용
        scale: 비율 (0.0 ~ 1.0), base_image_size 기준
        base_image_size: 기준 이미지 크기 (width, height)
    
    Returns:
        크기 조절된 로고 이미지
    """
    if target_size is not None:
        # 절대 크기 지정
        width, height = target_size
    elif scale is not None and base_image_size is not None:
        # 비율로 크기 계산
        base_width, base_height = base_image_size
        width = int(base_width * scale)
        height = int(base_height * scale)
    else:
        # 크기 조절 없음
        return logo
    
    # 최소 크기 보장
    width = max(1, width)
    height = max(1, height)
    
    # 비율 유지하며 크기 조절
    logo_h, logo_w = logo.shape[:2]
    aspect_ratio = logo_w / logo_h
    
    if width / height > aspect_ratio:
        # 높이 기준으로 조절
        new_height = height
        new_width = int(height * aspect_ratio)
    else:
        # 너비 기준으로 조절
        new_width = width
        new_height = int(width / aspect_ratio)
    
    # 크기 조절
    resized = cv2.resize(logo, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized


def add_logo(
    image: np.ndarray,
    logo_path: str,
    position: str = "bottom-right",
    scale: float = 0.1,
    margin: int = 20,
    opacity: float = 1.0
) -> np.ndarray:
    """
    이미지에 로고를 추가합니다.
    
    Args:
        image: 대상 이미지 (BGR 형식)
        logo_path: 로고 파일 경로
        position: 로고 위치 ('bottom-right', 'bottom-left', 'top-right', 'top-left')
        scale: 로고 크기 비율 (0.0 ~ 1.0, 기본값: 0.1)
        margin: 여백 (픽셀, 기본값: 20)
        opacity: 투명도 (0.0 ~ 1.0, 기본값: 1.0)
    
    Returns:
        로고가 추가된 이미지 (원본 수정)
    """
    # 로고 로드
    logo, has_alpha = load_logo(logo_path)
    
    # 이미지 크기
    img_h, img_w = image.shape[:2]
    
    # 로고 크기 조절
    logo = resize_logo(logo, scale=scale, base_image_size=(img_w, img_h))
    logo_h, logo_w = logo.shape[:2]
    
    # 위치 계산
    if position == "bottom-right":
        x = img_w - logo_w - margin
        y = img_h - logo_h - margin
    elif position == "bottom-left":
        x = margin
        y = img_h - logo_h - margin
    elif position == "top-right":
        x = img_w - logo_w - margin
        y = margin
    elif position == "top-left":
        x = margin
        y = margin
    else:
        # 기본값: bottom-right
        x = img_w - logo_w - margin
        y = img_h - logo_h - margin
    
    # 이미지 범위 내로 클리핑
    x = max(0, min(x, img_w - 1))
    y = max(0, min(y, img_h - 1))
    
    # 로고가 이미지 범위를 벗어나는 경우 크기 조절
    if x + logo_w > img_w:
        logo_w = img_w - x
        logo = cv2.resize(logo, (logo_w, logo_h), interpolation=cv2.INTER_AREA)
    if y + logo_h > img_h:
        logo_h = img_h - y
        logo = cv2.resize(logo, (logo_w, logo_h), interpolation=cv2.INTER_AREA)
    
    if logo_w <= 0 or logo_h <= 0:
        return image
    
    # ROI 추출
    roi = image[y:y+logo_h, x:x+logo_w]
    
    # 알파 채널이 있는 경우
    if has_alpha and logo.shape[2] == 4:
        # 알파 채널 분리
        logo_bgr = logo[:, :, :3]
        alpha = logo[:, :, 3:4] / 255.0  # 0.0 ~ 1.0
        
        # 투명도 적용
        alpha = alpha * opacity
        
        # 알파 블렌딩
        blended = (roi * (1 - alpha) + logo_bgr * alpha).astype(np.uint8)
        image[y:y+logo_h, x:x+logo_w] = blended
    else:
        # 알파 채널이 없는 경우 투명도 적용
        if opacity < 1.0:
            blended = cv2.addWeighted(roi, 1 - opacity, logo, opacity, 0)
            image[y:y+logo_h, x:x+logo_w] = blended
        else:
            # 투명도 1.0이면 그대로 덮어쓰기
            image[y:y+logo_h, x:x+logo_w] = logo
    
    return image
