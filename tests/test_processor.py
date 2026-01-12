"""
일괄 처리 모듈 테스트
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.processor import FaceMosaicProcessor


class TestFaceMosaicProcessor:
    """프로세서 테스트"""
    
    def test_init(self):
        """프로세서 초기화 테스트"""
        processor = FaceMosaicProcessor(detector_type="haar")
        assert processor is not None
        assert processor.method == "mosaic"
        assert processor.mosaic_size == 10  # 기본값이 10으로 변경됨
    
    def test_init_with_custom_params(self):
        """커스텀 파라미터로 초기화 테스트"""
        processor = FaceMosaicProcessor(
            detector_type="haar",
            method="blur",
            mosaic_size=20,
            blur_kernel_size=51,
            quality=90
        )
        assert processor.method == "blur"
        assert processor.mosaic_size == 20
        assert processor.blur_kernel_size == 51
        assert processor.quality == 90
    
    def test_process_image_no_face(self, tmp_path):
        """얼굴 없는 이미지 처리 테스트"""
        processor = FaceMosaicProcessor(detector_type="haar")
        
        # 테스트 이미지 생성 및 저장
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        import cv2
        input_path = tmp_path / "test.jpg"
        cv2.imwrite(str(input_path), test_image)
        
        output_path = tmp_path / "output.jpg"
        
        success, face_count = processor.process_image(str(input_path), str(output_path))
        
        assert success is True
        assert face_count == 0
        assert output_path.exists()
    
    def test_process_folder_empty(self, tmp_path):
        """빈 폴더 처리 테스트"""
        processor = FaceMosaicProcessor(detector_type="haar")
        
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        
        stats = processor.process_folder(str(input_dir), str(output_dir))
        
        assert stats["total"] == 0
        assert stats["success"] == 0
    
    def test_stats_initialization(self):
        """통계 초기화 테스트"""
        processor = FaceMosaicProcessor(detector_type="haar")
        
        assert processor.stats["total"] == 0
        assert processor.stats["success"] == 0
        assert processor.stats["failed"] == 0
        assert processor.stats["faces_detected"] == 0
