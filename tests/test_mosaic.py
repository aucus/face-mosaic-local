"""
모자이크 처리 모듈 테스트
"""

import numpy as np
import pytest

from src.mosaic import apply_mosaic, apply_blur, process_faces


class TestMosaic:
    """모자이크 테스트"""
    
    def test_apply_mosaic(self):
        """모자이크 적용 테스트"""
        # 다양한 픽셀 값을 가진 테스트 이미지 생성 (그라데이션)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            for j in range(100):
                image[i, j] = [i % 256, j % 256, (i + j) % 256]
        original = image.copy()
        bbox = (10, 10, 50, 50)
        
        result = apply_mosaic(image, bbox, block_size=10)
        
        assert result.shape == image.shape
        # 얼굴 영역이 변경되었는지 확인
        face_region_original = original[10:60, 10:60]
        face_region_result = result[10:60, 10:60]
        assert not np.array_equal(face_region_original, face_region_result)
    
    def test_apply_mosaic_out_of_bounds(self):
        """경계를 벗어나는 바운딩 박스 테스트"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        bbox = (90, 90, 50, 50)  # 이미지 범위를 벗어남
        
        # 에러 없이 처리되어야 함
        result = apply_mosaic(image, bbox, block_size=10)
        assert result.shape == image.shape
    
    def test_apply_mosaic_zero_size(self):
        """크기가 0인 바운딩 박스 테스트"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        bbox = (10, 10, 0, 0)
        
        result = apply_mosaic(image, bbox, block_size=10)
        assert result.shape == image.shape


class TestBlur:
    """블러 테스트"""
    
    def test_apply_blur(self):
        """블러 적용 테스트"""
        # 다양한 픽셀 값을 가진 테스트 이미지 생성 (그라데이션)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            for j in range(100):
                image[i, j] = [i % 256, j % 256, (i + j) % 256]
        original = image.copy()
        bbox = (10, 10, 50, 50)
        
        result = apply_blur(image, bbox, kernel_size=21)
        
        assert result.shape == image.shape
        # 얼굴 영역이 변경되었는지 확인
        face_region_original = original[10:60, 10:60]
        face_region_result = result[10:60, 10:60]
        assert not np.array_equal(face_region_original, face_region_result)
    
    def test_apply_blur_even_kernel(self):
        """짝수 커널 크기 테스트 (홀수로 변환되어야 함)"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        bbox = (10, 10, 50, 50)
        
        # 짝수 커널 크기
        result = apply_blur(image, bbox, kernel_size=20)
        assert result.shape == image.shape
    
    def test_apply_blur_out_of_bounds(self):
        """경계를 벗어나는 바운딩 박스 테스트"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        bbox = (90, 90, 50, 50)  # 이미지 범위를 벗어남
        
        result = apply_blur(image, bbox, kernel_size=21)
        assert result.shape == image.shape


class TestProcessFaces:
    """다중 얼굴 처리 테스트"""
    
    def test_process_faces_mosaic(self):
        """다중 얼굴 모자이크 처리 테스트"""
        # 다양한 픽셀 값을 가진 테스트 이미지 생성
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        for i in range(200):
            for j in range(200):
                image[i, j] = [i % 256, j % 256, (i + j) % 256]
        original = image.copy()
        bboxes = [(10, 10, 50, 50), (100, 100, 50, 50)]
        
        result = process_faces(image, bboxes, method="mosaic", block_size=10)
        
        assert result.shape == image.shape
        # 얼굴 영역이 변경되었는지 확인
        face1_original = original[10:60, 10:60]
        face1_result = result[10:60, 10:60]
        assert not np.array_equal(face1_original, face1_result)
    
    def test_process_faces_blur(self):
        """다중 얼굴 블러 처리 테스트"""
        # 다양한 픽셀 값을 가진 테스트 이미지 생성
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        for i in range(200):
            for j in range(200):
                image[i, j] = [i % 256, j % 256, (i + j) % 256]
        original = image.copy()
        bboxes = [(10, 10, 50, 50), (100, 100, 50, 50)]
        
        result = process_faces(image, bboxes, method="blur", kernel_size=21)
        
        assert result.shape == image.shape
        # 얼굴 영역이 변경되었는지 확인
        face1_original = original[10:60, 10:60]
        face1_result = result[10:60, 10:60]
        assert not np.array_equal(face1_original, face1_result)
    
    def test_process_faces_empty_list(self):
        """빈 얼굴 리스트 테스트"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        bboxes = []
        
        result = process_faces(image, bboxes, method="mosaic")
        
        assert result.shape == image.shape
        assert np.array_equal(result, image)  # 변경되지 않아야 함
    
    def test_process_faces_invalid_method(self):
        """잘못된 처리 방법 테스트"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        bboxes = [(10, 10, 50, 50)]
        
        with pytest.raises(ValueError):
            process_faces(image, bboxes, method="invalid")
