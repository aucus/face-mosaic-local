"""
일괄 처리 모듈

이미지 폴더를 일괄 처리하고 통계를 수집합니다.
"""

import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import cv2
import numpy as np
from tqdm import tqdm

from .detector import FaceDetector, get_detector
from .mosaic import process_faces
from .utils import get_image_files, load_image, save_image, setup_logger
from .watermark import add_logo


class FaceMosaicProcessor:
    """얼굴 모자이크 일괄 처리 클래스"""
    
    def __init__(
        self,
        detector_type: str = "dnn",
        detector_kwargs: Optional[Dict] = None,
        method: str = "mosaic",
        mosaic_size: int = 10,
        blur_kernel_size: int = 51,
        quality: int = 95,
        logo_path: Optional[str] = None,
        logo_scale: float = 0.2,  # 기본값 2배 증가 (0.1 → 0.2)
        logo_margin: int = 20,
        logo_opacity: float = 1.0
    ):
        """
        프로세서 초기화.
        
        Args:
            detector_type: 감지기 타입 ('haar' 또는 'dnn')
            detector_kwargs: 감지기별 추가 파라미터
            method: 처리 방법 ('mosaic' 또는 'blur')
            mosaic_size: 모자이크 블록 크기
            blur_kernel_size: 블러 커널 크기
            quality: 저장 품질 (1-100)
        """
        # 감지기 초기화
        detector_kwargs = detector_kwargs or {}
        self.detector: FaceDetector = get_detector(detector_type, **detector_kwargs)
        
        # 처리 설정
        self.method = method
        self.mosaic_size = mosaic_size
        self.blur_kernel_size = blur_kernel_size
        self.quality = quality
        
        # 로고 설정
        self.logo_path = logo_path
        self.logo_scale = logo_scale
        self.logo_margin = logo_margin
        self.logo_opacity = logo_opacity
        
        # 로거 설정
        self.logger = setup_logger("face_mosaic_processor")
        
        # 통계
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "faces_detected": 0,
            "processing_time": 0.0
        }
    
    def process_image(
        self,
        input_path: str,
        output_path: str
    ) -> Tuple[bool, int]:
        """
        단일 이미지를 처리합니다.
        
        Args:
            input_path: 입력 이미지 경로
            output_path: 출력 이미지 경로
        
        Returns:
            (성공 여부, 감지된 얼굴 수) 튜플
        """
        try:
            # 이미지 로드
            image, exif_data = load_image(input_path)
            
            # 얼굴 감지
            faces = self.detector.detect(image)
            
            # 얼굴이 감지된 경우에만 처리
            if faces:
                # 모자이크/블러 적용
                if self.method == "mosaic":
                    image = process_faces(image, faces, method="mosaic", block_size=self.mosaic_size)
                else:
                    image = process_faces(image, faces, method="blur", kernel_size=self.blur_kernel_size)
            
            # 로고 추가 (지정된 경우)
            if self.logo_path:
                try:
                    image = add_logo(
                        image,
                        self.logo_path,
                        position="bottom-right",
                        scale=self.logo_scale,
                        margin=self.logo_margin,
                        opacity=self.logo_opacity
                    )
                except Exception as e:
                    self.logger.warning(f"로고 추가 실패: {e}")
            
            # 이미지 저장
            save_image(image, output_path, quality=self.quality, exif_data=exif_data)
            
            return True, len(faces)
        
        except Exception as e:
            self.logger.error(f"이미지 처리 실패: {input_path} - {e}")
            return False, 0
    
    def process_folder(
        self,
        input_dir: str,
        output_dir: str,
        recursive: bool = False
    ) -> Dict:
        """
        폴더 내 모든 이미지를 일괄 처리합니다.
        
        Args:
            input_dir: 입력 폴더 경로
            output_dir: 출력 폴더 경로
            recursive: 하위 폴더까지 재귀적으로 처리할지 여부
        
        Returns:
            처리 통계 딕셔너리
        """
        # 통계 초기화
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "faces_detected": 0,
            "processing_time": 0.0
        }
        
        start_time = time.time()
        
        # 이미지 파일 목록 가져오기
        try:
            image_files = get_image_files(input_dir, recursive=recursive)
        except Exception as e:
            self.logger.error(f"이미지 파일 목록 가져오기 실패: {e}")
            return self.stats
        
        self.stats["total"] = len(image_files)
        
        if self.stats["total"] == 0:
            self.logger.warning(f"처리할 이미지가 없습니다: {input_dir}")
            return self.stats
        
        # 출력 폴더 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"처리 시작: {self.stats['total']}개 이미지")
        
        # 진행률 표시와 함께 처리
        for image_file in tqdm(image_files, desc="처리 중", unit="장"):
            # 상대 경로 유지 (재귀 처리 시)
            if recursive:
                relative_path = image_file.relative_to(Path(input_dir))
                output_file = output_path / relative_path
            else:
                output_file = output_path / image_file.name
            
            # 출력 디렉토리 생성
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 이미지 처리
            success, face_count = self.process_image(str(image_file), str(output_file))
            
            if success:
                self.stats["success"] += 1
                self.stats["faces_detected"] += face_count
                
                if face_count == 0:
                    self.stats["skipped"] += 1  # 얼굴이 없는 이미지
            else:
                self.stats["failed"] += 1
        
        # 처리 시간 계산
        self.stats["processing_time"] = time.time() - start_time
        
        # 결과 리포트 출력
        self._print_report()
        
        return self.stats
    
    def _print_report(self) -> None:
        """처리 결과 리포트를 출력합니다."""
        stats = self.stats
        
        self.logger.info("=" * 50)
        self.logger.info("처리 완료 리포트")
        self.logger.info("=" * 50)
        self.logger.info(f"총 이미지: {stats['total']}장")
        self.logger.info(f"성공: {stats['success']}장")
        self.logger.info(f"실패: {stats['failed']}장")
        self.logger.info(f"스킵 (얼굴 없음): {stats['skipped']}장")
        self.logger.info(f"감지된 얼굴: {stats['faces_detected']}개")
        self.logger.info(f"처리 시간: {stats['processing_time']:.2f}초")
        
        if stats['total'] > 0:
            avg_time = stats['processing_time'] / stats['total']
            self.logger.info(f"평균 처리 시간: {avg_time:.2f}초/장")
        
        self.logger.info("=" * 50)
