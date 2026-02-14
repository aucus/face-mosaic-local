#!/usr/bin/env python3
"""
Face Mosaic Local - 수동 모자이크 지정 GUI

마우스 드래그로 영역을 직접 지정하여 모자이크를 적용하는 기능
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QSlider, QSpinBox,
    QGroupBox, QDoubleSpinBox, QLineEdit, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QMouseEvent

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import get_image_files, load_image, save_image
from src.mosaic import apply_mosaic, apply_blur
from src.watermark import add_logo


class ImageLabel(QLabel):
    """이미지 표시 및 마우스 드래그 영역 선택을 위한 커스텀 QLabel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.setMinimumSize(400, 300)
        
        # 드래그 상태
        self.dragging = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        
        # 선택된 영역 리스트 [(x, y, w, h), ...]
        self.selected_regions: List[Tuple[int, int, int, int]] = []
        
        # 원본 이미지 (BGR)
        self.original_image: Optional[np.ndarray] = None
        # 표시용 이미지 (RGB, QPixmap으로 변환)
        self.display_image: Optional[QPixmap] = None
        # 이미지 스케일 (원본 대비 표시 크기)
        self.image_scale = 1.0
        # 이미지 오프셋 (중앙 정렬)
        self.image_offset = QPoint(0, 0)
    
    def set_image(self, image: np.ndarray):
        """이미지를 설정하고 표시"""
        self.original_image = image.copy()
        
        # BGR → RGB 변환
        if len(image.shape) == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # QImage로 변환
        h, w = rgb_image.shape[:2]
        bytes_per_line = 3 * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # QPixmap으로 변환
        self.display_image = QPixmap.fromImage(q_image)
        
        # 이미지 크기에 맞게 스케일 계산
        self.update_image_scale()
        
        # 영역 초기화
        self.selected_regions = []
        self.update_display()
    
    def update_image_scale(self):
        """이미지 스케일 계산 (윈도우 크기에 맞춤)"""
        if self.display_image is None:
            return
        
        label_size = self.size()
        image_size = self.display_image.size()
        
        # 윈도우에 맞게 스케일 계산 (비율 유지)
        scale_x = (label_size.width() - 20) / image_size.width()
        scale_y = (label_size.height() - 20) / image_size.height()
        self.image_scale = min(scale_x, scale_y, 1.0)  # 확대하지 않음
        
        # 스케일된 이미지 크기
        scaled_width = int(image_size.width() * self.image_scale)
        scaled_height = int(image_size.height() * self.image_scale)
        
        # 중앙 정렬 오프셋
        self.image_offset = QPoint(
            (label_size.width() - scaled_width) // 2,
            (label_size.height() - scaled_height) // 2
        )
    
    def screen_to_image_coords(self, screen_point: QPoint) -> QPoint:
        """화면 좌표를 이미지 좌표로 변환"""
        if self.image_scale == 0:
            return QPoint(0, 0)
        
        # 화면 좌표에서 이미지 오프셋 제거
        image_point = QPoint(
            screen_point.x() - self.image_offset.x(),
            screen_point.y() - self.image_offset.y()
        )
        
        # 스케일 역변환
        image_point = QPoint(
            int(image_point.x() / self.image_scale),
            int(image_point.y() / self.image_scale)
        )
        
        # 이미지 범위 내로 클리핑
        if self.original_image is not None:
            h, w = self.original_image.shape[:2]
            image_point = QPoint(
                max(0, min(image_point.x(), w - 1)),
                max(0, min(image_point.y(), h - 1))
            )
        
        return image_point
    
    def image_to_screen_coords(self, image_point: QPoint) -> QPoint:
        """이미지 좌표를 화면 좌표로 변환"""
        screen_point = QPoint(
            int(image_point.x() * self.image_scale) + self.image_offset.x(),
            int(image_point.y() * self.image_scale) + self.image_offset.y()
        )
        return screen_point
    
    def mousePressEvent(self, event: QMouseEvent):
        """마우스 버튼 누름"""
        if event.button() == Qt.LeftButton:
            # 드래그 시작
            self.dragging = True
            self.start_point = self.screen_to_image_coords(event.pos())
            self.end_point = self.start_point
            self.update_display()
        elif event.button() == Qt.RightButton:
            # 우클릭: 가장 가까운 영역 삭제
            click_point = self.screen_to_image_coords(event.pos())
            self.remove_nearest_region(click_point)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """마우스 이동"""
        if self.dragging:
            self.end_point = self.screen_to_image_coords(event.pos())
            self.update_display()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """마우스 버튼 놓음"""
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            # 영역 추가
            self.add_region()
            self.update_display()
    
    def add_region(self):
        """현재 드래그 영역을 리스트에 추가"""
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        # 정규화 (x1 < x2, y1 < y2)
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        
        # 최소 크기 체크 (너무 작은 영역은 무시)
        if w >= 10 and h >= 10:
            self.selected_regions.append((x, y, w, h))
    
    def remove_nearest_region(self, point: QPoint):
        """가장 가까운 영역 삭제"""
        if not self.selected_regions:
            return
        
        px, py = point.x(), point.y()
        min_dist = float('inf')
        nearest_idx = -1
        
        for idx, (x, y, w, h) in enumerate(self.selected_regions):
            # 영역 중심점
            cx = x + w // 2
            cy = y + h // 2
            # 거리 계산
            dist = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_idx = idx
        
        # 영역 내부 클릭 확인 (거리 < 영역 대각선의 절반)
        if nearest_idx >= 0:
            x, y, w, h = self.selected_regions[nearest_idx]
            diagonal = (w ** 2 + h ** 2) ** 0.5
            if min_dist < diagonal / 2:
                self.selected_regions.pop(nearest_idx)
                self.update_display()
    
    def clear_regions(self):
        """모든 선택 영역 제거"""
        self.selected_regions = []
        self.update_display()
    
    def resizeEvent(self, event):
        """윈도우 크기 변경"""
        super().resizeEvent(event)
        self.update_image_scale()
        self.update_display()
    
    def update_display(self):
        """이미지와 선택 영역을 그려서 표시"""
        if self.display_image is None:
            self.clear()
            return
        
        # 스케일된 이미지 생성
        scaled_pixmap = self.display_image.scaled(
            int(self.display_image.width() * self.image_scale),
            int(self.display_image.height() * self.image_scale),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # QPixmap에 그리기
        painter = QPainter(scaled_pixmap)
        
        # 선택된 영역 그리기
        pen = QPen(QColor(255, 0, 0), 2)  # 빨간색, 두께 2
        painter.setPen(pen)
        
        for x, y, w, h in self.selected_regions:
            # 이미지 좌표를 화면 좌표로 변환
            screen_x = int(x * self.image_scale)
            screen_y = int(y * self.image_scale)
            screen_w = int(w * self.image_scale)
            screen_h = int(h * self.image_scale)
            painter.drawRect(screen_x, screen_y, screen_w, screen_h)
        
        # 드래그 중인 영역 그리기
        if self.dragging:
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            screen_x = int(x * self.image_scale)
            screen_y = int(y * self.image_scale)
            screen_w = int(w * self.image_scale)
            screen_h = int(h * self.image_scale)
            painter.drawRect(screen_x, screen_y, screen_w, screen_h)
        
        painter.end()
        
        # QLabel에 표시
        self.setPixmap(scaled_pixmap)


class ManualMosaicWidget(QWidget):
    """수동 모자이크 지정 위젯 (임베드 가능)"""
    
    def __init__(
        self,
        parent=None,
        show_folder_controls: bool = True,
        show_logo_controls: bool = True,
        embed_controls: bool = True
    ):
        super().__init__(parent)
        self.show_folder_controls = show_folder_controls
        self.show_logo_controls = show_logo_controls
        self.embed_controls = embed_controls
        
        # 변수
        self.input_folder = ""
        self.output_folder = ""
        self.image_files: List[Path] = []
        self.current_image_index = -1
        self.current_image: Optional[np.ndarray] = None
        self.current_exif: Optional[dict] = None
        self.method = "mosaic"  # "mosaic" or "blur"
        self.mosaic_size = 15
        self.blur_kernel_size = 51
        self.logo_path = ""
        self.logo_scale = 0.2
        self.logo_margin = 20
        self.logo_opacity = 1.0
        
        # PyInstaller 빌드 앱에서는 사용자 홈 디렉토리 사용
        if hasattr(sys, '_MEIPASS'):
            default_output = str(Path.home() / "Desktop" / "FaceMosaicOutput")
        else:
            default_output = str(Path.cwd() / "output")
        self.output_folder = default_output
        
        # UI 구성
        self.setup_ui()
    
    def setup_ui(self):
        """UI 구성"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 상단: 폴더 선택 및 정보 표시
        top_layout = QHBoxLayout()
        
        if self.show_folder_controls:
            # 입력 폴더 선택
            btn_input = QPushButton("입력 폴더 선택")
            btn_input.clicked.connect(self.select_input_folder)
            top_layout.addWidget(btn_input)
            
            # 출력 폴더 선택
            btn_output = QPushButton("출력 폴더 선택")
            btn_output.clicked.connect(self.select_output_folder)
            top_layout.addWidget(btn_output)
            
            self.output_folder_label = QLabel(f"출력: {self.output_folder}")
            self.output_folder_label.setStyleSheet("color: #666; font-size: 11px;")
            top_layout.addWidget(self.output_folder_label)
            
            top_layout.addStretch()
        else:
            # 임베드 모드: 상단 최소화 (이미지 정보만 표시)
            self.output_folder_label = None
        
        self.image_info_label = QLabel("이미지를 선택하세요")
        top_layout.addWidget(self.image_info_label)
        
        if self.show_folder_controls:
            # 독립 창 모드에서는 상단에 네비게이션 표시
            btn_prev = QPushButton("◀ 이전")
            btn_prev.clicked.connect(self.prev_image)
            btn_prev.setEnabled(False)
            self.btn_prev = btn_prev
            top_layout.addWidget(btn_prev)
            
            btn_next = QPushButton("다음 ▶")
            btn_next.clicked.connect(self.next_image)
            btn_next.setEnabled(False)
            self.btn_next = btn_next
            top_layout.addWidget(btn_next)
        else:
            # 임베드 모드에서는 하단으로 이동
            self.btn_prev = QPushButton("◀ 이전")
            self.btn_prev.clicked.connect(self.prev_image)
            self.btn_prev.setEnabled(False)
            self.btn_next = QPushButton("다음 ▶")
            self.btn_next.clicked.connect(self.next_image)
            self.btn_next.setEnabled(False)
        
        main_layout.addLayout(top_layout)
        
        # 이미지 표시 영역
        self.image_label = ImageLabel()
        main_layout.addWidget(self.image_label, stretch=1)
        
        # 컨트롤 영역 (옵션/버튼)
        self.controls_widget = QWidget()
        bottom_layout = QVBoxLayout(self.controls_widget)
        
        # 처리 방법 선택
        method_group = QGroupBox("처리 방법")
        method_layout = QVBoxLayout(method_group)
        
        method_radio_layout = QHBoxLayout()
        self.method_group = QButtonGroup()
        self.mosaic_radio = QRadioButton("모자이크")
        self.blur_radio = QRadioButton("가우시안 블러 (흐림 효과)")
        self.mosaic_radio.setChecked(True)
        self.method_group.addButton(self.mosaic_radio, 0)
        self.method_group.addButton(self.blur_radio, 1)
        self.mosaic_radio.toggled.connect(self.on_method_changed)
        self.blur_radio.toggled.connect(self.on_method_changed)
        method_radio_layout.addWidget(self.mosaic_radio)
        method_radio_layout.addWidget(self.blur_radio)
        method_radio_layout.addStretch()
        method_layout.addLayout(method_radio_layout)
        
        # 모자이크 크기 조절
        self.mosaic_size_layout = QHBoxLayout()
        self.mosaic_size_label_widget = QLabel("모자이크 크기:")
        self.mosaic_size_layout.addWidget(self.mosaic_size_label_widget)
        self.mosaic_slider = QSlider(Qt.Horizontal)
        self.mosaic_slider.setMinimum(1)
        self.mosaic_slider.setMaximum(50)
        self.mosaic_slider.setValue(15)
        self.mosaic_slider.valueChanged.connect(self.update_mosaic_size)
        self.mosaic_size_layout.addWidget(self.mosaic_slider)
        self.mosaic_size_label = QLabel("15")
        self.mosaic_size_label.setMinimumWidth(30)
        self.mosaic_size_layout.addWidget(self.mosaic_size_label)
        method_layout.addLayout(self.mosaic_size_layout)
        
        # 블러 커널 크기 조절
        self.blur_size_layout = QHBoxLayout()
        self.blur_size_label_widget = QLabel("블러 강도:")
        self.blur_size_layout.addWidget(self.blur_size_label_widget)
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setMinimum(5)
        self.blur_slider.setMaximum(101)
        self.blur_slider.setValue(51)
        self.blur_slider.setSingleStep(2)  # 홀수만
        self.blur_slider.valueChanged.connect(self.update_blur_size)
        self.blur_size_layout.addWidget(self.blur_slider)
        self.blur_size_label = QLabel("51")
        self.blur_size_label.setMinimumWidth(30)
        self.blur_size_layout.addWidget(self.blur_size_label)
        method_layout.addLayout(self.blur_size_layout)
        
        # 초기에는 블러 레이아웃 숨김
        self.blur_size_label_widget.setVisible(False)
        self.blur_slider.setVisible(False)
        self.blur_size_label.setVisible(False)
        
        bottom_layout.addWidget(method_group)
        
        if self.show_logo_controls:
            # 로고 설정 (선택사항)
            logo_group = QGroupBox("로고 설정 (선택사항)")
            logo_layout = QVBoxLayout(logo_group)
            
            # 로고 파일 선택
            logo_file_layout = QHBoxLayout()
            logo_file_layout.addWidget(QLabel("로고 파일:"))
            self.logo_path_edit = QLineEdit()
            self.logo_path_edit.setPlaceholderText("로고 파일을 선택하세요 (선택사항)")
            logo_file_layout.addWidget(self.logo_path_edit)
            btn_logo = QPushButton("선택")
            btn_logo.clicked.connect(self.select_logo)
            logo_file_layout.addWidget(btn_logo)
            logo_layout.addLayout(logo_file_layout)
            
            # 로고 크기
            logo_scale_layout = QHBoxLayout()
            logo_scale_layout.addWidget(QLabel("로고 크기:"))
            self.logo_scale_spin = QDoubleSpinBox()
            self.logo_scale_spin.setMinimum(0.05)
            self.logo_scale_spin.setMaximum(1.0)
            self.logo_scale_spin.setSingleStep(0.05)
            self.logo_scale_spin.setValue(0.2)
            self.logo_scale_spin.setDecimals(2)
            self.logo_scale_spin.valueChanged.connect(self.update_logo_scale)
            logo_scale_layout.addWidget(self.logo_scale_spin)
            logo_scale_layout.addStretch()
            logo_layout.addLayout(logo_scale_layout)
            
            # 로고 여백
            logo_margin_layout = QHBoxLayout()
            logo_margin_layout.addWidget(QLabel("로고 여백:"))
            self.logo_margin_spin = QSpinBox()
            self.logo_margin_spin.setMinimum(0)
            self.logo_margin_spin.setMaximum(100)
            self.logo_margin_spin.setValue(20)
            self.logo_margin_spin.valueChanged.connect(self.update_logo_margin)
            logo_margin_layout.addWidget(self.logo_margin_spin)
            logo_margin_layout.addStretch()
            logo_layout.addLayout(logo_margin_layout)
            
            # 로고 투명도
            logo_opacity_layout = QHBoxLayout()
            logo_opacity_layout.addWidget(QLabel("로고 투명도:"))
            self.logo_opacity_spin = QDoubleSpinBox()
            self.logo_opacity_spin.setMinimum(0.0)
            self.logo_opacity_spin.setMaximum(1.0)
            self.logo_opacity_spin.setSingleStep(0.1)
            self.logo_opacity_spin.setValue(1.0)
            self.logo_opacity_spin.setDecimals(1)
            self.logo_opacity_spin.valueChanged.connect(self.update_logo_opacity)
            logo_opacity_layout.addWidget(self.logo_opacity_spin)
            logo_opacity_layout.addStretch()
            logo_layout.addLayout(logo_opacity_layout)
            
            bottom_layout.addWidget(logo_group)
        else:
            self.logo_path_edit = None
            self.logo_scale_spin = None
            self.logo_margin_spin = None
            self.logo_opacity_spin = None
        
        # 버튼 영역 (2x2 그리드)
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 상단 줄: 이전/다음 버튼
        top_button_row = QHBoxLayout()
        top_button_row.setSpacing(10)
        
        # 임베드 모드: 네비게이션 버튼을 하단에 배치
        if not self.show_folder_controls:
            # 버튼 텍스트가 잘 보이도록 최소 폭 확보 + 글자 크기 축소
            self.btn_prev.setMinimumWidth(70)
            self.btn_next.setMinimumWidth(70)
            self.btn_prev.setStyleSheet("font-size: 12px;")
            self.btn_next.setStyleSheet("font-size: 12px;")
            top_button_row.addWidget(self.btn_prev)
            top_button_row.addWidget(self.btn_next)
        
        top_button_row.addStretch()
        button_layout.addLayout(top_button_row)
        
        # 하단 줄: 영역 초기화/저장 버튼
        bottom_button_row = QHBoxLayout()
        bottom_button_row.setSpacing(10)
        
        btn_clear = QPushButton("영역 초기화")
        btn_clear.clicked.connect(self.clear_regions)
        btn_clear.setMinimumWidth(120)
        btn_clear.setMaximumWidth(120)
        btn_clear.setStyleSheet("font-size: 12px;")
        bottom_button_row.addWidget(btn_clear)
        
        bottom_button_row.addStretch()
        
        btn_save = QPushButton("저장")
        btn_save.setMinimumWidth(80)
        btn_save.setMaximumWidth(80)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.save_image)
        bottom_button_row.addWidget(btn_save)
        
        button_layout.addLayout(bottom_button_row)
        
        bottom_layout.addWidget(button_container)
        if self.embed_controls:
            main_layout.addWidget(self.controls_widget)
    
    def on_method_changed(self):
        """처리 방법 변경"""
        if self.mosaic_radio.isChecked():
            self.method = "mosaic"
            # 모자이크 크기 레이아웃 표시
            self.mosaic_size_label_widget.setVisible(True)
            self.mosaic_slider.setVisible(True)
            self.mosaic_size_label.setVisible(True)
            # 블러 크기 레이아웃 숨김
            self.blur_size_label_widget.setVisible(False)
            self.blur_slider.setVisible(False)
            self.blur_size_label.setVisible(False)
        elif self.blur_radio.isChecked():
            self.method = "blur"
            # 모자이크 크기 레이아웃 숨김
            self.mosaic_size_label_widget.setVisible(False)
            self.mosaic_slider.setVisible(False)
            self.mosaic_size_label.setVisible(False)
            # 블러 크기 레이아웃 표시
            self.blur_size_label_widget.setVisible(True)
            self.blur_slider.setVisible(True)
            self.blur_size_label.setVisible(True)
    
    def update_mosaic_size(self, value: int):
        """모자이크 크기 업데이트"""
        self.mosaic_size = value
        self.mosaic_size_label.setText(str(value))
    
    def update_blur_size(self, value: int):
        """블러 커널 크기 업데이트 (홀수로 보정)"""
        # 홀수로 보정
        if value % 2 == 0:
            value += 1
            self.blur_slider.setValue(value)
        self.blur_kernel_size = value
        self.blur_size_label.setText(str(value))
    
    def select_logo(self):
        """로고 파일 선택"""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "로고 파일 선택",
            "",
            "이미지 파일 (*.png *.jpg *.jpeg);;모든 파일 (*.*)"
        )
        if file:
            self.logo_path = file
            if self.logo_path_edit is not None:
                self.logo_path_edit.setText(file)
    
    def update_logo_scale(self, value: float):
        """로고 크기 업데이트"""
        self.logo_scale = value
    
    def update_logo_margin(self, value: int):
        """로고 여백 업데이트"""
        self.logo_margin = value
    
    def update_logo_opacity(self, value: float):
        """로고 투명도 업데이트"""
        self.logo_opacity = value
    
    def set_input_folder(self, folder: str) -> None:
        """외부에서 입력 폴더 설정"""
        self.input_folder = folder
        if folder:
            self.load_folder(folder)
    
    def set_output_folder(self, folder: str) -> None:
        """외부에서 출력 폴더 설정"""
        self.output_folder = folder
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
            if self.output_folder_label is not None:
                self.output_folder_label.setText(f"출력: {folder}")
    
    def set_logo_settings(self, logo_path: str, scale: float, margin: int, opacity: float) -> None:
        """외부에서 로고 설정 전달"""
        self.logo_path = logo_path
        self.logo_scale = scale
        self.logo_margin = margin
        self.logo_opacity = opacity
        if self.logo_path_edit is not None:
            self.logo_path_edit.setText(logo_path or "")
        if self.logo_scale_spin is not None:
            self.logo_scale_spin.setValue(scale)
        if self.logo_margin_spin is not None:
            self.logo_margin_spin.setValue(margin)
        if self.logo_opacity_spin is not None:
            self.logo_opacity_spin.setValue(opacity)
    
    def select_input_folder(self):
        """입력 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(self, "입력 폴더 선택", self.input_folder)
        if folder:
            self.load_folder(folder)
    
    def load_folder(self, folder: str):
        """폴더에서 이미지 목록 로드"""
        self.input_folder = folder
        try:
            self.image_files = get_image_files(folder)
            if not self.image_files:
                QMessageBox.warning(self, "경고", "선택한 폴더에 이미지 파일이 없습니다.")
                return
            
            # 첫 번째 이미지 로드
            self.current_image_index = 0
            self.load_image(0)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"폴더를 읽는 중 오류가 발생했습니다:\n{str(e)}")
    
    def select_output_folder(self):
        """출력 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택", self.output_folder)
        if folder:
            self.output_folder = folder
            # 출력 폴더 생성
            Path(folder).mkdir(parents=True, exist_ok=True)
            # UI 업데이트
            self.output_folder_label.setText(f"출력: {folder}")
    
    def load_image(self, index: int):
        """이미지 로드"""
        if index < 0 or index >= len(self.image_files):
            return
        
        try:
            image_path = self.image_files[index]
            image, exif = load_image(str(image_path))
            self.current_image = image
            self.current_exif = exif
            self.current_image_index = index
            
            # 이미지 표시 (선택 영역 초기화)
            self.image_label.set_image(image)
            
            # 네비게이션 버튼 업데이트
            self.btn_prev.setEnabled(index > 0)
            self.btn_next.setEnabled(index < len(self.image_files) - 1)
            
            # 이미지 정보 업데이트
            self.image_info_label.setText(
                f"{index + 1} / {len(self.image_files)} - {image_path.name}"
            )
        except Exception as e:
            QMessageBox.critical(self, "오류", f"이미지를 로드하는 중 오류가 발생했습니다:\n{str(e)}")
    
    def prev_image(self):
        """이전 이미지"""
        if self.current_image_index > 0:
            if self._check_unsaved_changes():
                self.load_image(self.current_image_index - 1)

    def next_image(self):
        """다음 이미지"""
        if self.current_image_index < len(self.image_files) - 1:
            if self._check_unsaved_changes():
                self.load_image(self.current_image_index + 1)
    
    def clear_regions(self):
        """선택 영역 초기화"""
        self.image_label.clear_regions()

    def _check_unsaved_changes(self) -> bool:
        """
        미저장 변경사항 확인.

        Returns:
            True: 진행해도 됨 (변경 없음 / 사용자가 허용)
            False: 진행 취소
        """
        if not self.image_label.selected_regions:
            return True

        reply = QMessageBox.question(
            self,
            "미저장 경고",
            "선택한 모자이크 영역이 저장되지 않았습니다.\n저장하지 않고 이동하시겠습니까?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_image()
            return True
        elif reply == QMessageBox.Discard:
            return True
        else:  # Cancel
            return False

    def save_image(self):
        """처리된 이미지 저장"""
        if self.current_image is None:
            QMessageBox.warning(self, "경고", "이미지가 로드되지 않았습니다.")
            return
        
        if not self.output_folder:
            QMessageBox.warning(self, "경고", "출력 폴더를 선택해주세요.")
            return
        
        # 선택된 영역이 없고 로고도 없으면 경고
        logo_path_text = self.logo_path
        if self.logo_path_edit is not None:
            text = self.logo_path_edit.text().strip()
            if text:
                logo_path_text = text
                self.logo_path = text
        if not self.image_label.selected_regions and not logo_path_text:
            QMessageBox.warning(
                self,
                "경고",
                "선택된 영역이 없고 로고도 선택되지 않았습니다.\n"
                "모자이크를 적용하거나 로고를 선택해주세요."
            )
            return
        
        try:
            # 이미지 복사
            processed_image = self.current_image.copy()
            
            # 선택된 영역에 처리 적용 (모자이크 또는 블러)
            for x, y, w, h in self.image_label.selected_regions:
                if self.method == "mosaic":
                    apply_mosaic(processed_image, (x, y, w, h), block_size=self.mosaic_size)
                elif self.method == "blur":
                    apply_blur(processed_image, (x, y, w, h), kernel_size=self.blur_kernel_size)
            
            # 로고 추가 (선택사항)
            if logo_path_text:
                logo_path_obj = Path(logo_path_text)
                if logo_path_obj.exists():
                    add_logo(
                        processed_image,
                        str(logo_path_obj),
                        position="bottom-right",
                        scale=self.logo_scale,
                        margin=self.logo_margin,
                        opacity=self.logo_opacity
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "경고",
                        f"로고 파일을 찾을 수 없습니다:\n{logo_path_text}\n\n로고 없이 저장합니다."
                    )
            
            # 저장 경로
            image_path = self.image_files[self.current_image_index]
            output_path = Path(self.output_folder) / image_path.name
            
            # 저장
            save_image(processed_image, str(output_path), quality=95, exif_data=self.current_exif)
            
            # 완료 메시지
            method_name = "모자이크" if self.method == "mosaic" else "블러"
            message = f"이미지가 저장되었습니다:\n{output_path}\n\n"
            if self.image_label.selected_regions:
                message += f"처리된 영역: {len(self.image_label.selected_regions)}개 ({method_name})\n"
            if logo_path_text:
                message += "로고 추가됨"
            QMessageBox.information(self, "완료", message)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"이미지를 저장하는 중 오류가 발생했습니다:\n{str(e)}")


class ManualMosaicWindow(QMainWindow):
    """수동 모자이크 지정 메인 윈도우"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("수동 모자이크 지정 - Face Mosaic Local")
        # 창 크기와 위치 설정 (메인 창 옆에 표시)
        self.setGeometry(150, 150, 1000, 800)
        # 창이 독립적으로 표시되도록 설정
        if parent is None:
            self.setWindowFlags(Qt.Window)
        
        self.manual_widget = ManualMosaicWidget(
            self,
            show_folder_controls=True,
            show_logo_controls=True
        )
        self.setCentralWidget(self.manual_widget)
    
    def set_input_folder(self, folder: str) -> None:
        """입력 폴더 전달"""
        self.manual_widget.set_input_folder(folder)
    
    def set_output_folder(self, folder: str) -> None:
        """출력 폴더 전달"""
        self.manual_widget.set_output_folder(folder)
    
    def set_logo_settings(self, logo_path: str, scale: float, margin: int, opacity: float) -> None:
        """로고 설정 전달"""
        self.manual_widget.set_logo_settings(logo_path, scale, margin, opacity)

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    window = ManualMosaicWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
