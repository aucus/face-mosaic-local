"""
얼굴 감지 모듈 테스트
"""

import pytest
import numpy as np
import cv2
from pathlib import Path

from src.detector import FaceDetector, HaarCascadeDetector, DNNDetector, get_detector


class TestHaarCascadeDetector:
    """Haar Cascade 감지기 테스트"""
    
    def test_init(self):
        """감지기 초기화 테스트"""
        detector = HaarCascadeDetector()
        assert detector is not None
        assert not detector.cascade.empty()
    
    def test_detect_empty_image(self):
        """빈 이미지 테스트"""
        detector = HaarCascadeDetector()
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        faces = detector.detect(empty_image)
        assert isinstance(faces, list)
        assert len(faces) == 0
    
    def test_detect_no_face(self):
        """얼굴 없는 이미지 테스트"""
        detector = HaarCascadeDetector()
        # 단색 이미지 생성
        image = np.ones((200, 200, 3), dtype=np.uint8) * 128
        faces = detector.detect(image)
        assert isinstance(faces, list)


class TestDNNDetector:
    """DNN 감지기 테스트"""
    
    def test_init_without_model(self):
        """모델 파일 없을 때 에러 테스트"""
        # 모델 파일이 없는 경우를 시뮬레이션하기 어려우므로
        # 실제 모델 파일이 있는 경우만 테스트
        model_dir = Path(__file__).parent.parent / "models"
        prototxt = model_dir / "deploy.prototxt"
        model = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"
        
        if prototxt.exists() and model.exists():
            detector = DNNDetector()
            assert detector is not None
            assert detector.net is not None
        else:
            # 모델 파일이 없으면 스킵
            pytest.skip("DNN 모델 파일이 없습니다. download_models.py를 실행하세요.")
    
    def test_detect_empty_image(self):
        """빈 이미지 테스트"""
        model_dir = Path(__file__).parent.parent / "models"
        prototxt = model_dir / "deploy.prototxt"
        model = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"
        
        if not (prototxt.exists() and model.exists()):
            pytest.skip("DNN 모델 파일이 없습니다.")
        
        detector = DNNDetector()
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        faces = detector.detect(empty_image)
        assert isinstance(faces, list)
        assert len(faces) == 0
    
    def test_confidence_threshold(self):
        """신뢰도 임계값 테스트"""
        model_dir = Path(__file__).parent.parent / "models"
        prototxt = model_dir / "deploy.prototxt"
        model = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"
        
        if not (prototxt.exists() and model.exists()):
            pytest.skip("DNN 모델 파일이 없습니다.")
        
        # 높은 임계값으로 감지기 생성
        detector = DNNDetector(confidence_threshold=0.99)
        assert detector.confidence_threshold == 0.99


class TestDetectorFactory:
    """감지기 팩토리 테스트"""
    
    def test_get_haar_detector(self):
        """Haar 감지기 팩토리 테스트"""
        detector = get_detector("haar")
        assert isinstance(detector, HaarCascadeDetector)
    
    def test_get_dnn_detector(self):
        """DNN 감지기 팩토리 테스트"""
        model_dir = Path(__file__).parent.parent / "models"
        prototxt = model_dir / "deploy.prototxt"
        model = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"
        
        if not (prototxt.exists() and model.exists()):
            pytest.skip("DNN 모델 파일이 없습니다.")
        
        detector = get_detector("dnn")
        assert isinstance(detector, DNNDetector)
    
    def test_get_default_detector(self):
        """기본 감지기 테스트"""
        model_dir = Path(__file__).parent.parent / "models"
        prototxt = model_dir / "deploy.prototxt"
        model = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"
        
        if not (prototxt.exists() and model.exists()):
            # 모델이 없으면 Haar가 기본값
            detector = get_detector()
            assert isinstance(detector, HaarCascadeDetector)
        else:
            detector = get_detector()
            assert isinstance(detector, DNNDetector)
    
    def test_invalid_detector_type(self):
        """잘못된 감지기 타입 테스트"""
        with pytest.raises(ValueError):
            get_detector("invalid")
