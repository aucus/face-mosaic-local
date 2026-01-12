"""
워터마크/로고 추가 모듈 테스트
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import cv2

from src.watermark import load_logo, resize_logo, add_logo


class TestLoadLogo:
    """로고 로드 테스트"""
    
    def test_load_nonexistent_logo(self):
        """존재하지 않는 로고 파일 테스트"""
        with pytest.raises(FileNotFoundError):
            load_logo("nonexistent.png")
    
    def test_load_logo_with_alpha(self, tmp_path):
        """알파 채널이 있는 로고 로드 테스트"""
        # RGBA 이미지 생성
        logo_array = np.zeros((100, 100, 4), dtype=np.uint8)
        logo_array[:, :, :3] = 255  # 흰색
        logo_array[:, :, 3] = 128  # 반투명
        
        logo_path = tmp_path / "logo.png"
        cv2.imwrite(str(logo_path), logo_array)
        
        logo, has_alpha = load_logo(str(logo_path))
        
        assert has_alpha is True
        assert logo.shape[2] == 4  # BGRA
    
    def test_load_logo_without_alpha(self, tmp_path):
        """알파 채널이 없는 로고 로드 테스트"""
        # RGB 이미지 생성
        logo_array = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        logo_path = tmp_path / "logo.jpg"
        cv2.imwrite(str(logo_path), logo_array)
        
        logo, has_alpha = load_logo(str(logo_path))
        
        assert has_alpha is False
        assert logo.shape[2] == 3  # BGR


class TestResizeLogo:
    """로고 크기 조절 테스트"""
    
    def test_resize_by_scale(self):
        """비율로 크기 조절 테스트"""
        logo = np.ones((100, 100, 3), dtype=np.uint8) * 128
        base_size = (1000, 1000)
        
        resized = resize_logo(logo, scale=0.1, base_image_size=base_size)
        
        assert resized.shape[0] == 100  # 높이
        assert resized.shape[1] == 100  # 너비
    
    def test_resize_by_target_size(self):
        """목표 크기로 조절 테스트"""
        logo = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        resized = resize_logo(logo, target_size=(50, 50))
        
        assert resized.shape[0] == 50
        assert resized.shape[1] == 50
    
    def test_resize_maintain_aspect_ratio(self):
        """비율 유지 테스트"""
        logo = np.ones((200, 100, 3), dtype=np.uint8) * 128  # 2:1 비율
        
        resized = resize_logo(logo, target_size=(50, 50))
        
        # 비율 유지되어야 함
        aspect_ratio = resized.shape[1] / resized.shape[0]
        assert abs(aspect_ratio - 0.5) < 0.1  # 2:1 비율


class TestAddLogo:
    """로고 추가 테스트"""
    
    def test_add_logo_bottom_right(self, tmp_path):
        """우측 하단에 로고 추가 테스트"""
        # 테스트 이미지 생성
        image = np.ones((500, 500, 3), dtype=np.uint8) * 128
        
        # 로고 생성
        logo = np.ones((50, 50, 3), dtype=np.uint8) * 255
        logo_path = tmp_path / "logo.png"
        cv2.imwrite(str(logo_path), logo)
        
        result = add_logo(image.copy(), str(logo_path), position="bottom-right", margin=20)
        
        assert result.shape == image.shape
        # 우측 하단 영역이 변경되었는지 확인
        bottom_right = result[430:480, 430:480]
        assert not np.array_equal(bottom_right, image[430:480, 430:480])
    
    def test_add_logo_with_opacity(self, tmp_path):
        """투명도 적용 테스트"""
        image = np.ones((500, 500, 3), dtype=np.uint8) * 128
        logo = np.ones((50, 50, 3), dtype=np.uint8) * 255
        logo_path = tmp_path / "logo.png"
        cv2.imwrite(str(logo_path), logo)
        
        result = add_logo(image.copy(), str(logo_path), opacity=0.5)
        
        assert result.shape == image.shape
    
    def test_add_logo_different_positions(self, tmp_path):
        """다양한 위치 테스트"""
        image = np.ones((500, 500, 3), dtype=np.uint8) * 128
        logo = np.ones((50, 50, 3), dtype=np.uint8) * 255
        logo_path = tmp_path / "logo.png"
        cv2.imwrite(str(logo_path), logo)
        
        positions = ["bottom-right", "bottom-left", "top-right", "top-left"]
        
        for position in positions:
            result = add_logo(image.copy(), str(logo_path), position=position)
            assert result.shape == image.shape
    
    def test_add_logo_with_alpha_channel(self, tmp_path):
        """알파 채널이 있는 로고 추가 테스트"""
        image = np.ones((500, 500, 3), dtype=np.uint8) * 128
        
        # RGBA 로고 생성
        logo_rgba = np.zeros((50, 50, 4), dtype=np.uint8)
        logo_rgba[:, :, :3] = 255
        logo_rgba[:, :, 3] = 128  # 반투명
        
        logo_path = tmp_path / "logo.png"
        cv2.imwrite(str(logo_path), logo_rgba)
        
        result = add_logo(image.copy(), str(logo_path))
        
        assert result.shape == image.shape
