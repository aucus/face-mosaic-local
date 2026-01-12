"""
얼굴 감지 모듈

OpenCV를 사용한 얼굴 감지 기능을 제공합니다.
Haar Cascade와 DNN 두 가지 방식을 지원합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from pathlib import Path
import cv2
import numpy as np


class FaceDetector(ABC):
    """얼굴 감지기 베이스 클래스"""
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        이미지에서 얼굴을 감지합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
        
        Returns:
            얼굴 바운딩 박스 리스트 [(x, y, width, height), ...]
        """
        pass


class HaarCascadeDetector(FaceDetector):
    """Haar Cascade 기반 얼굴 감지기"""
    
    def __init__(self, scale_factor: float = 1.1, min_neighbors: int = 5, min_size: Tuple[int, int] = (30, 30)):
        """
        Haar Cascade 감지기 초기화.
        
        Args:
            scale_factor: 이미지 스케일 감소 비율
            min_neighbors: 최소 이웃 수
            min_size: 최소 얼굴 크기 (width, height)
        """
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.cascade.empty():
            raise RuntimeError("Haar Cascade 파일을 로드할 수 없습니다.")
        
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
    
    def detect(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Haar Cascade를 사용하여 얼굴을 감지합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
        
        Returns:
            얼굴 바운딩 박스 리스트 [(x, y, width, height), ...]
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )
        
        # numpy array를 튜플 리스트로 변환
        return [tuple(map(int, face)) for face in faces]


class DNNDetector(FaceDetector):
    """DNN 기반 얼굴 감지기 (SSD + ResNet)"""
    
    def __init__(self, confidence_threshold: float = 0.5, model_dir: str = "models"):
        """
        DNN 감지기 초기화.
        
        Args:
            confidence_threshold: 신뢰도 임계값 (0.0 ~ 1.0)
            model_dir: 모델 파일이 있는 디렉토리
        """
        self.confidence_threshold = confidence_threshold
        
        # 모델 파일 경로
        model_dir_path = Path(__file__).parent.parent / model_dir
        prototxt_path = model_dir_path / "deploy.prototxt"
        model_path = model_dir_path / "res10_300x300_ssd_iter_140000.caffemodel"
        
        # 파일 존재 확인
        if not prototxt_path.exists():
            raise FileNotFoundError(
                f"모델 파일을 찾을 수 없습니다: {prototxt_path}\n"
                f"다운로드 스크립트를 실행하세요: python download_models.py"
            )
        if not model_path.exists():
            raise FileNotFoundError(
                f"모델 파일을 찾을 수 없습니다: {model_path}\n"
                f"다운로드 스크립트를 실행하세요: python download_models.py"
            )
        
        # 모델 로드
        self.net = cv2.dnn.readNetFromCaffe(str(prototxt_path), str(model_path))
        
        # 입력 이미지 크기 (DNN 모델이 300x300으로 학습됨)
        self.input_size = (300, 300)
        self.scale_factor = 1.0
        self.mean = (104.0, 177.0, 123.0)  # BGR 평균값
    
    def detect(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        DNN을 사용하여 얼굴을 감지합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
        
        Returns:
            얼굴 바운딩 박스 리스트 [(x, y, width, height), ...]
        """
        h, w = image.shape[:2]
        
        # blob 생성 (전처리)
        blob = cv2.dnn.blobFromImage(
            image,
            scalefactor=self.scale_factor,
            size=self.input_size,
            mean=self.mean
        )
        
        # 네트워크에 입력
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # 신뢰도 임계값 이상인 경우만 처리
            if confidence > self.confidence_threshold:
                # 바운딩 박스 좌표 계산 (0.0 ~ 1.0 → 픽셀 좌표)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x, y, x2, y2 = box.astype(int)
                
                # width, height로 변환
                width = x2 - x
                height = y2 - y
                
                # 이미지 범위 내로 클리핑
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                width = min(width, w - x)
                height = min(height, h - y)
                
                faces.append((x, y, width, height))
        
        return faces


def get_detector(detector_type: str = "dnn", **kwargs) -> FaceDetector:
    """
    감지기 팩토리 함수.
    
    Args:
        detector_type: 감지기 타입 ('haar' 또는 'dnn')
        **kwargs: 감지기별 추가 파라미터
    
    Returns:
        FaceDetector 인스턴스
    
    Raises:
        ValueError: 지원하지 않는 감지기 타입인 경우
    """
    detector_type = detector_type.lower()
    
    if detector_type == "haar":
        return HaarCascadeDetector(**kwargs)
    elif detector_type == "dnn":
        return DNNDetector(**kwargs)
    else:
        raise ValueError(f"지원하지 않는 감지기 타입: {detector_type} (haar 또는 dnn)")
