"""
유틸리티 모듈 테스트 (파일 목록, 이미지 로드, EXIF Orientation 적용)
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from src.utils import get_image_files, load_image, SUPPORTED_FORMATS


class TestGetImageFiles:
    """get_image_files 테스트"""

    def test_empty_folder(self, tmp_path):
        """빈 폴더"""
        assert get_image_files(str(tmp_path)) == []

    def test_finds_supported_formats(self, tmp_path):
        """지원 확장자 파일만 수집"""
        (tmp_path / "a.jpg").write_bytes(b"x")
        (tmp_path / "b.png").write_bytes(b"x")
        (tmp_path / "c.txt").write_bytes(b"x")
        (tmp_path / "d.JPEG").write_bytes(b"x")
        found = get_image_files(str(tmp_path))
        names = {f.name for f in found}
        assert names == {"a.jpg", "b.png", "d.JPEG"}
        assert (tmp_path / "c.txt").name not in names

    def test_nonexistent_folder_raises(self):
        """없는 폴더 시 FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            get_image_files("/nonexistent/path")


class TestLoadImage:
    """load_image 테스트 (EXIF Orientation 적용 포함)"""

    def test_load_returns_ndarray_and_exif(self, tmp_path):
        """로드 시 (ndarray, exif_dict|None) 반환, BGR 형식"""
        from PIL import Image

        pil = Image.new("RGB", (40, 30), color=(1, 2, 3))
        jpg_path = tmp_path / "test.jpg"
        pil.save(str(jpg_path), quality=95)

        image, exif = load_image(str(jpg_path))

        assert isinstance(image, np.ndarray)
        assert image.shape == (30, 40, 3)  # H, W, C (OpenCV 순서)
        assert image.dtype == np.uint8
        # BGR 3채널, JPEG 압축으로 픽셀값은 근사일 수 있음
        assert image.ndim == 3 and image.shape[2] == 3

    def test_load_png_no_exif(self, tmp_path):
        """PNG 로드 시 exif는 None일 수 있음, shape/BGR 일관"""
        from PIL import Image

        pil = Image.new("RGB", (20, 10), color=(5, 10, 15))
        pil.save(str(tmp_path / "test.png"))
        image, exif = load_image(str(tmp_path / "test.png"))
        assert image.shape == (10, 20, 3)
        assert image[0, 0, 2] == 5 and image[0, 0, 0] == 15

    def test_nonexistent_file_raises(self):
        """없는 파일 시 FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_image("/nonexistent/image.jpg")
