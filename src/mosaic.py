"""
모자이크 및 블러 처리 모듈

감지된 얼굴 영역에 모자이크 또는 블러 효과를 적용합니다.
"""

from typing import List, Tuple, Literal
import cv2
import numpy as np


def apply_mosaic(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    block_size: int = 10
) -> np.ndarray:
    """
    얼굴 영역에 모자이크 효과를 적용합니다.
    
    더 자연스러운 모자이크 효과를 위해 큰 블록 크기를 사용하고,
    약간의 블러를 추가하여 경계를 부드럽게 만듭니다.
    
    Args:
        image: 입력 이미지 (BGR 형식)
        bbox: 바운딩 박스 (x, y, width, height)
        block_size: 모자이크 블록 크기 (픽셀, 작을수록 블록이 큼, 기본값: 10)
                    예: block_size=10이면 100x100 영역이 10x10으로 축소되어 큰 블록 생성
    
    Returns:
        처리된 이미지 (원본 수정)
    """
    x, y, w, h = bbox
    h_img, w_img = image.shape[:2]
    
    # 이미지 범위 내로 클리핑
    x = max(0, min(x, w_img - 1))
    y = max(0, min(y, h_img - 1))
    w = min(w, w_img - x)
    h = min(h, h_img - y)
    
    if w <= 0 or h <= 0:
        return image
    
    # 얼굴 영역 추출
    face_roi = image[y:y+h, x:x+w].copy()
    
    # 축소 → 확대 (모자이크 효과)
    # block_size가 작을수록 축소된 크기가 커지고, 확대 시 더 큰 블록이 됨
    small_w = max(1, w // block_size)
    small_h = max(1, h // block_size)
    
    # 축소 시 INTER_AREA 사용 (더 나은 품질)
    small = cv2.resize(face_roi, (small_w, small_h), interpolation=cv2.INTER_AREA)
    
    # 확대 시 INTER_NEAREST로 모자이크 효과 유지
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    
    # 더 자연스러운 경계를 위해 약간의 블러 추가
    # 블러 강도는 블록 크기에 비례 (작은 block_size는 큰 블록이므로 더 많은 블러)
    blur_size = max(3, block_size // 3)
    if blur_size % 2 == 0:
        blur_size += 1
    mosaic = cv2.GaussianBlur(mosaic, (blur_size, blur_size), 0)
    
    # 원본 이미지에 적용
    image[y:y+h, x:x+w] = mosaic
    
    return image


def apply_blur(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    kernel_size: int = 51
) -> np.ndarray:
    """
    얼굴 영역에 Gaussian 블러 효과를 적용합니다.
    
    Args:
        image: 입력 이미지 (BGR 형식)
        bbox: 바운딩 박스 (x, y, width, height)
        kernel_size: 블러 커널 크기 (홀수만 가능)
    
    Returns:
        처리된 이미지 (원본 수정)
    """
    x, y, w, h = bbox
    h_img, w_img = image.shape[:2]
    
    # 이미지 범위 내로 클리핑
    x = max(0, min(x, w_img - 1))
    y = max(0, min(y, h_img - 1))
    w = min(w, w_img - x)
    h = min(h, h_img - y)
    
    if w <= 0 or h <= 0:
        return image
    
    # 커널 크기 유효성 검사 (홀수만 가능)
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # 얼굴 영역 추출
    face_roi = image[y:y+h, x:x+w]
    
    # Gaussian 블러 적용
    blurred = cv2.GaussianBlur(face_roi, (kernel_size, kernel_size), 0)
    
    # 원본 이미지에 적용
    image[y:y+h, x:x+w] = blurred
    
    return image


def process_faces(
    image: np.ndarray,
    bboxes: List[Tuple[int, int, int, int]],
    method: Literal["mosaic", "blur"] = "mosaic",
    **kwargs
) -> np.ndarray:
    """
    이미지의 여러 얼굴에 모자이크 또는 블러를 적용합니다.
    
    Args:
        image: 입력 이미지 (BGR 형식, 복사본 사용)
        bboxes: 얼굴 바운딩 박스 리스트
        method: 처리 방법 ('mosaic' 또는 'blur')
        **kwargs: 처리 방법별 추가 파라미터
            - mosaic: block_size (기본값: 10, 작을수록 블록이 큼)
            - blur: kernel_size (기본값: 51)
    
    Returns:
        처리된 이미지
    """
    # 원본 이미지 복사 (원본 보호)
    result = image.copy()
    
    # 각 얼굴에 처리 적용
    for bbox in bboxes:
        if method == "mosaic":
            block_size = kwargs.get("block_size", 10)
            apply_mosaic(result, bbox, block_size)
        elif method == "blur":
            kernel_size = kwargs.get("kernel_size", 51)
            apply_blur(result, bbox, kernel_size)
        else:
            raise ValueError(f"지원하지 않는 처리 방법: {method} (mosaic 또는 blur)")
    
    return result
