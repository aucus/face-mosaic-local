#!/usr/bin/env python3
"""
Face Mosaic Local - GUI 메인 윈도우 (PySide6)

PySide6 기반 그래픽 사용자 인터페이스
macOS 26.2 호환성 문제 해결
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QProgressBar, QTextEdit, QGroupBox, QRadioButton, QButtonGroup,
    QSlider, QDoubleSpinBox, QSpinBox, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processor import FaceMosaicProcessor
from src.utils import setup_logger
from gui.manual_mosaic_window import ManualMosaicWidget


class ProcessingThread(QThread):
    """이미지 처리를 백그라운드에서 실행하는 스레드"""
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, processor, input_folder, output_folder):
        super().__init__()
        self.processor = processor
        self.input_folder = input_folder
        self.output_folder = output_folder
    
    def run(self):
        try:
            self.progress.emit("처리 시작...")
            stats = self.processor.process_folder(self.input_folder, self.output_folder)
            self.finished.emit(stats)
        except Exception as e:
            self.error.emit(str(e))


class FaceMosaicGUI(QMainWindow):
    """Face Mosaic Local GUI 클래스"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Mosaic Local")
        self.setGeometry(100, 100, 900, 800)
        
        # 변수
        self.input_folder = ""
        # PyInstaller 빌드 앱에서는 사용자 홈 디렉토리 사용
        if hasattr(sys, '_MEIPASS'):
            # 빌드된 앱인 경우
            default_output = str(Path.home() / "Desktop" / "FaceMosaicOutput")
        else:
            # 개발 모드
            default_output = str(Path.cwd() / "output")
        self.output_folder = default_output
        self.detector_type = "dnn"
        self.method = "mosaic"
        self.mosaic_size = 10
        self.confidence = 0.5
        self.logo_path = ""
        self.logo_scale = 0.2  # 기본값 2배 증가 (0.1 → 0.2)
        self.logo_margin = 20
        self.logo_opacity = 1.0
        
        # 처리 중 플래그
        self.processing = False
        self.processing_thread = None
        
        # 로거 설정
        self.logger = setup_logger("face_mosaic_gui")
        
        # UI 구성
        self.setup_ui()
    
    def setup_ui(self):
        """UI 구성"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(18, 18, 18, 18)
        
        # 제목
        title_label = QLabel("Face Mosaic Local")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 탭 메뉴 (자동/수동)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        auto_page = QWidget()
        auto_layout = QVBoxLayout(auto_page)
        auto_hint = QLabel("자동 처리 옵션은 우측 패널에서 설정하세요.")
        auto_hint.setStyleSheet("color: #888;")
        auto_layout.addWidget(auto_hint)
        auto_layout.addStretch()
        self.tabs.addTab(auto_page, "자동 처리")
        
        manual_page = QWidget()
        manual_layout = QVBoxLayout(manual_page)
        self.manual_widget = ManualMosaicWidget(
            show_folder_controls=False,
            show_logo_controls=False,
            embed_controls=False
        )
        manual_layout.addWidget(self.manual_widget, stretch=1)
        self.tabs.addTab(manual_page, "수동 지정")
        
        # 본문 레이아웃 (좌: 탭, 우: 컨트롤 패널)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)
        body_layout.addWidget(self.tabs, stretch=1)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(10)
        
        # 입력/출력 폴더
        folder_group = QGroupBox("입력/출력")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setContentsMargins(10, 8, 10, 8)
        folder_layout.setSpacing(6)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)
        input_layout.addWidget(QLabel("입력:"))
        self.input_folder_edit = QLineEdit()
        self.input_folder_edit.setPlaceholderText("입력 폴더를 선택하세요")
        self.input_folder_edit.editingFinished.connect(self.on_input_folder_edited)
        input_layout.addWidget(self.input_folder_edit)
        btn_input = QPushButton("선택")
        btn_input.clicked.connect(self.select_input_folder)
        input_layout.addWidget(btn_input)
        folder_layout.addLayout(input_layout)
        
        output_layout = QHBoxLayout()
        output_layout.setSpacing(6)
        output_layout.addWidget(QLabel("출력:"))
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setText(self.output_folder)
        self.output_folder_edit.editingFinished.connect(self.on_output_folder_edited)
        output_layout.addWidget(self.output_folder_edit)
        btn_output = QPushButton("선택")
        btn_output.clicked.connect(self.select_output_folder)
        output_layout.addWidget(btn_output)
        folder_layout.addLayout(output_layout)
        
        right_layout.addWidget(folder_group)
        
        # 로고 설정 (공통)
        logo_group = QGroupBox("로고 설정 (공통)")
        logo_group.setMaximumHeight(180)  # 높이를 1/2로 제한
        logo_layout = QVBoxLayout(logo_group)
        logo_layout.setContentsMargins(8, 6, 8, 6)
        logo_layout.setSpacing(6)
        
        logo_file_layout = QHBoxLayout()
        logo_file_layout.addWidget(QLabel("로고 파일:"))
        self.logo_path_edit = QLineEdit()
        self.logo_path_edit.setPlaceholderText("로고 파일을 선택하세요 (선택사항)")
        logo_file_layout.addWidget(self.logo_path_edit)
        btn_logo = QPushButton("선택")
        btn_logo.clicked.connect(self.select_logo)
        logo_file_layout.addWidget(btn_logo)
        logo_layout.addLayout(logo_file_layout)
        
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
        
        right_layout.addWidget(logo_group)
        
        # 컨트롤 스택 (자동/수동)
        self.controls_stack = QTabWidget()
        self.controls_stack.tabBar().hide()
        
        auto_controls = QWidget()
        auto_controls_layout = QVBoxLayout(auto_controls)
        
        options_group = QGroupBox("자동 처리 옵션")
        options_layout = QVBoxLayout(options_group)
        
        detector_layout = QHBoxLayout()
        detector_layout.addWidget(QLabel("감지기:"))
        self.detector_group = QButtonGroup()
        self.haar_radio = QRadioButton("Haar Cascade")
        self.dnn_radio = QRadioButton("DNN (권장)")
        self.dnn_radio.setChecked(True)
        self.detector_group.addButton(self.haar_radio, 0)
        self.detector_group.addButton(self.dnn_radio, 1)
        detector_layout.addWidget(self.haar_radio)
        detector_layout.addWidget(self.dnn_radio)
        detector_layout.addStretch()
        options_layout.addLayout(detector_layout)
        
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("처리 방법:"))
        self.method_group = QButtonGroup()
        self.mosaic_radio = QRadioButton("모자이크")
        self.blur_radio = QRadioButton("블러")
        self.mosaic_radio.setChecked(True)
        self.method_group.addButton(self.mosaic_radio, 0)
        self.method_group.addButton(self.blur_radio, 1)
        method_layout.addWidget(self.mosaic_radio)
        method_layout.addWidget(self.blur_radio)
        method_layout.addStretch()
        options_layout.addLayout(method_layout)
        
        mosaic_layout = QHBoxLayout()
        mosaic_layout.addWidget(QLabel("모자이크 크기:"))
        self.mosaic_slider = QSlider(Qt.Horizontal)
        self.mosaic_slider.setMinimum(1)
        self.mosaic_slider.setMaximum(50)
        self.mosaic_slider.setValue(10)
        self.mosaic_slider.valueChanged.connect(self.update_mosaic_size_label)
        mosaic_layout.addWidget(self.mosaic_slider)
        self.mosaic_size_label = QLabel("10")
        self.mosaic_size_label.setMinimumWidth(30)
        mosaic_layout.addWidget(self.mosaic_size_label)
        options_layout.addLayout(mosaic_layout)
        
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("신뢰도:"))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(1)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(50)
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        confidence_layout.addWidget(self.confidence_slider)
        self.confidence_label = QLabel("0.50")
        self.confidence_label.setMinimumWidth(40)
        confidence_layout.addWidget(self.confidence_label)
        options_layout.addLayout(confidence_layout)
        
        auto_controls_layout.addWidget(options_group)
        
        self.process_button = QPushButton("자동 처리 시작")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.process_button.clicked.connect(self.start_processing)
        auto_controls_layout.addWidget(self.process_button)
        
        self.controls_stack.addTab(auto_controls, "auto")
        
        manual_controls = QWidget()
        manual_controls_layout = QVBoxLayout(manual_controls)
        manual_controls_layout.addWidget(self.manual_widget.controls_widget)
        self.controls_stack.addTab(manual_controls, "manual")
        
        right_layout.addWidget(self.controls_stack)
        
        # 상태 + 로그
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("준비됨")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(20)
        right_layout.addWidget(self.status_label)
        
        log_group = QGroupBox("로그")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(8, 6, 8, 6)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)
        right_layout.addWidget(log_group, stretch=1)
        
        right_panel.setFixedWidth(360)
        body_layout.addWidget(right_panel)
        
        main_layout.addLayout(body_layout)
        
        # 탭 전환 시 우측 컨트롤 변경
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.on_tab_changed(0)
        
        # 초기 상태 동기화
        self.sync_manual_settings()
        
        # 초기 로그
        self.log("Face Mosaic Local GUI 시작")
        self.log("상단 탭에서 자동/수동 모드를 선택하세요.")
    
    def update_mosaic_size_label(self, value):
        """모자이크 크기 레이블 업데이트"""
        self.mosaic_size_label.setText(str(value))
        self.mosaic_size = value

    def on_tab_changed(self, index: int) -> None:
        """탭 변경 시 우측 컨트롤 전환"""
        if hasattr(self, "controls_stack"):
            self.controls_stack.setCurrentIndex(index)
        if index == 1:
            # 수동 모드 진입 시 폴더/로고 동기화
            if self.input_folder:
                self.manual_widget.set_input_folder(self.input_folder)
            self.manual_widget.set_output_folder(self.output_folder)
            self.sync_manual_settings()
    
    def update_confidence_label(self, value):
        """신뢰도 레이블 업데이트"""
        confidence = value / 100.0
        self.confidence_label.setText(f"{confidence:.2f}")
        self.confidence = confidence
    
    def select_input_folder(self):
        """입력 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(self, "입력 폴더 선택")
        if folder:
            self.input_folder = folder
            self.input_folder_edit.setText(folder)
            self.log(f"입력 폴더: {folder}")
            self.manual_widget.set_input_folder(folder)
    
    def select_output_folder(self):
        """출력 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder:
            self.output_folder = folder
            self.output_folder_edit.setText(folder)
            self.log(f"출력 폴더: {folder}")
            self.manual_widget.set_output_folder(folder)
    
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
            self.logo_path_edit.setText(file)
            self.log(f"로고 파일: {file}")
            self.sync_manual_settings()
    
    def update_logo_scale(self, value: float):
        """로고 크기 업데이트"""
        self.logo_scale = value
        self.sync_manual_settings()
    
    def update_logo_margin(self, value: int):
        """로고 여백 업데이트"""
        self.logo_margin = value
        self.sync_manual_settings()
    
    def update_logo_opacity(self, value: float):
        """로고 투명도 업데이트"""
        self.logo_opacity = value
        self.sync_manual_settings()
    
    def on_input_folder_edited(self):
        """입력 폴더 직접 입력 처리"""
        folder = self.input_folder_edit.text().strip()
        if folder:
            self.input_folder = folder
            self.manual_widget.set_input_folder(folder)
    
    def on_output_folder_edited(self):
        """출력 폴더 직접 입력 처리"""
        folder = self.output_folder_edit.text().strip()
        if folder:
            self.output_folder = folder
            self.manual_widget.set_output_folder(folder)
    
    def sync_manual_settings(self):
        """수동 위젯에 공통 설정 전달"""
        self.manual_widget.set_output_folder(self.output_folder)
        self.manual_widget.set_logo_settings(
            self.logo_path,
            self.logo_scale,
            self.logo_margin,
            self.logo_opacity
        )
    
    def log(self, message: str):
        """로그 메시지 추가"""
        self.log_text.append(message)
        # 스크롤을 맨 아래로
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def validate_inputs(self) -> bool:
        """입력값 검증"""
        if not self.input_folder:
            QMessageBox.warning(self, "오류", "입력 폴더를 선택해주세요.")
            return False
        
        input_path = Path(self.input_folder)
        if not input_path.exists():
            QMessageBox.warning(self, "오류", f"입력 폴더가 존재하지 않습니다: {input_path}")
            return False
        
        if not input_path.is_dir():
            QMessageBox.warning(self, "오류", f"입력 경로가 폴더가 아닙니다: {input_path}")
            return False
        
        if self.logo_path:
            logo_path = Path(self.logo_path)
            if not logo_path.exists():
                QMessageBox.warning(self, "오류", f"로고 파일이 존재하지 않습니다: {logo_path}")
                return False
        
        return True
    
    def start_processing(self):
        """처리 시작"""
        if self.processing:
            QMessageBox.warning(self, "경고", "이미 처리 중입니다.")
            return
        
        if not self.validate_inputs():
            return
        
        # 옵션 값 가져오기
        self.detector_type = "haar" if self.haar_radio.isChecked() else "dnn"
        self.method = "blur" if self.blur_radio.isChecked() else "mosaic"
        self.mosaic_size = self.mosaic_slider.value()
        self.confidence = self.confidence_slider.value() / 100.0
        # 출력 폴더 경로 처리 (상대 경로를 절대 경로로 변환)
        output_folder_text = self.output_folder_edit.text().strip()
        if not output_folder_text:
            # 기본값 설정
            if hasattr(sys, '_MEIPASS'):
                output_folder_text = str(Path.home() / "Desktop" / "FaceMosaicOutput")
            else:
                output_folder_text = str(Path.cwd() / "output")
        
        # 상대 경로를 절대 경로로 변환
        output_path = Path(output_folder_text)
        if not output_path.is_absolute():
            if hasattr(sys, '_MEIPASS'):
                # 빌드된 앱: 홈 디렉토리 기준
                output_path = Path.home() / output_folder_text
            else:
                # 개발 모드: 현재 작업 디렉토리 기준
                output_path = Path.cwd() / output_folder_text
        
        # 출력 폴더 생성
        output_path.mkdir(parents=True, exist_ok=True)
        self.output_folder = str(output_path)
        self.logo_path = self.logo_path_edit.text() or ""
        self.logo_scale = self.logo_scale_spin.value()
        self.logo_margin = self.logo_margin_spin.value()
        
        # 프로세서 생성
        detector_kwargs = {}
        if self.detector_type == "dnn":
            detector_kwargs["confidence_threshold"] = self.confidence
        
        processor = FaceMosaicProcessor(
            detector_type=self.detector_type,
            detector_kwargs=detector_kwargs,
            method=self.method,
            mosaic_size=self.mosaic_size,
            quality=95,
            logo_path=self.logo_path if self.logo_path else None,
            logo_scale=self.logo_scale,
            logo_margin=self.logo_margin,
            logo_opacity=self.logo_opacity
        )
        
        # 처리 시작
        self.processing = True
        self.process_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 무한 진행
        self.status_label.setText("처리 중...")
        
        self.log(f"처리 시작: {self.input_folder} → {self.output_folder}")
        self.log(f"감지기: {self.detector_type}, 방법: {self.method}")
        
        # 백그라운드 스레드에서 처리
        self.processing_thread = ProcessingThread(processor, self.input_folder, self.output_folder)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.progress.connect(self.log)
        self.processing_thread.start()
    
    def on_processing_finished(self, stats: dict):
        """처리 완료"""
        self.processing = False
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("처리 완료!")
        
        self.log("=" * 50)
        self.log("처리 완료!")
        self.log(f"총 이미지: {stats['total']}장")
        self.log(f"성공: {stats['success']}장")
        self.log(f"실패: {stats['failed']}장")
        self.log(f"감지된 얼굴: {stats['faces_detected']}개")
        self.log(f"처리 시간: {stats['processing_time']:.2f}초")
        
        QMessageBox.information(
            self,
            "완료",
            f"처리가 완료되었습니다!\n\n"
            f"성공: {stats['success']}장\n"
            f"감지된 얼굴: {stats['faces_detected']}개"
        )
    
    def on_processing_error(self, error_msg: str):
        """처리 오류"""
        self.processing = False
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("오류 발생")
        
        self.log(f"오류: {error_msg}")
        QMessageBox.critical(self, "오류", f"처리 중 오류가 발생했습니다:\n\n{error_msg}")
    
    def closeEvent(self, event):
        """윈도우 종료 이벤트"""
        if self.processing:
            reply = QMessageBox.question(
                self,
                "종료 확인",
                "처리 중입니다. 정말 종료하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            if self.processing_thread and self.processing_thread.isRunning():
                self.processing_thread.terminate()
                self.processing_thread.wait()
        
        event.accept()


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    window = FaceMosaicGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
