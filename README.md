# 🖼️ Face Mosaic Local

> 폴더째로 드래그하면 얼굴 모자이크 끝! 완전 오프라인, 프라이버시 보장

로컬 기반 얼굴 모자이크 처리 프로그램입니다.

## 💰 무료 vs Pro

| | 무료 | Pro (₩9,900) |
|---|---|---|
| 배치 처리 | 5장/회 | 무제한 |
| 워터마크 | 있음 | 없음 |
| GUI + CLI | ✅ | ✅ |
| 오프라인 동작 | ✅ | ✅ |
| **구매** | [네이버 스마트스토어](https://smartstore.naver.com/)에서 Pro 구매 | |

> ⚠️ macOS/Windows에서 "확인되지 않은 개발자" 또는 SmartScreen 경고가 나타나면  
> [설치 가이드](./docs/INSTALL_GUIDE.md)를 참고하세요.

## ✨ 특징

- **완전 무료**: API 비용 없이 로컬에서 처리
- **프라이버시**: 이미지가 외부 서버로 전송되지 않음
- **오프라인**: 인터넷 연결 없이 동작
- **빠른 처리**: 1초/장 (1080p 기준)
- **다중 얼굴 감지**: 한 이미지에서 여러 얼굴 동시 처리
- **EXIF 메타데이터 보존**: 원본 이미지 메타데이터 유지

## 📋 요구사항

- Python 3.9 이상
- OpenCV 4.8 이상
- NumPy 1.24 이상
- Pillow 10.0 이상
- tqdm 4.65 이상

## 🚀 설치

### 1. 저장소 클론

```bash
git clone <repository-url>
cd face-mosaic-local
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (macOS/Linux)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 개발 환경 설정 (테스트/빌드 포함)

```bash
pip install -r requirements-dev.txt
```

### 4. DNN 모델 다운로드 (DNN 감지기 사용 시 필수)

DNN 감지기를 사용하려면 모델 파일을 다운로드해야 합니다:

```bash
python download_models.py
```

모델 파일은 `models/` 폴더에 저장됩니다.

## 📖 사용법

### 기본 사용

```bash
python -m src.main --input ./photos --output ./output
```

### 옵션 지정

```bash
python -m src.main \
  --input ./photos \
  --output ./output \
  --detector dnn \
  --mosaic-size 15 \
  --method mosaic \
  --confidence 0.5
```

### CLI 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--input` | 입력 폴더 경로 (필수) | - |
| `--output` | 출력 폴더 경로 | `./output` |
| `--detector` | 감지기 타입 (`haar` 또는 `dnn`) | `dnn` |
| `--mosaic-size` | 모자이크 블록 크기 | `15` |
| `--method` | 처리 방법 (`mosaic` 또는 `blur`) | `mosaic` |
| `--confidence` | DNN 신뢰도 임계값 (0.0-1.0) | `0.5` |
| `--blur-kernel-size` | 블러 커널 크기 | `51` |
| `--quality` | 저장 품질 (1-100) | `95` |
| `--recursive` | 하위 폴더까지 재귀 처리 | `False` |
| `--log-file` | 로그 파일 경로 | 없음 |

### Python 모듈로 사용

```python
from src.processor import FaceMosaicProcessor

# 프로세서 생성
processor = FaceMosaicProcessor(
    detector_type='dnn',
    method='mosaic',
    mosaic_size=15
)

# 폴더 처리
stats = processor.process_folder('./photos', './output')

print(f"처리 완료: {stats['success']}장 성공, {stats['faces_detected']}개 얼굴 감지")
```

### GUI 사용

```bash
# GUI 실행
python -m gui.main_window
```

GUI 화면에서:
1. **입력 폴더 선택**: "입력 폴더 선택" 버튼 클릭
2. **출력 폴더 선택**: "출력 폴더 선택" 버튼 클릭
3. **옵션 설정**:
   - 감지기: Haar / DNN 선택
   - 처리 방법: 모자이크 / 블러 선택
   - 모자이크 크기: 슬라이더로 조절 (1-50)
   - 신뢰도: 슬라이더로 조절 (0.1-1.0)
   - 로고 파일: 선택 (선택사항)
4. **처리 시작**: "처리 시작" 버튼 클릭
5. **진행 상황**: 프로그레스 바와 로그 영역에서 확인

## 🔧 얼굴 감지 방식

### Haar Cascade (기본)

- **장점**: 가볍고 빠름, 추가 모델 다운로드 불필요
- **단점**: 정확도 낮음, 측면/기울어진 얼굴 감지 어려움
- **사용법**: `--detector haar`

### DNN (SSD + ResNet) ⭐ 권장

- **장점**: 높은 정확도, 다양한 각도 지원
- **단점**: 모델 파일 다운로드 필요 (~10MB)
- **사용법**: `--detector dnn` (기본값)

## 📊 성능

| 항목 | 목표값 |
|------|--------|
| 처리 속도 | 1초/장 (1080p 기준) |
| 메모리 사용 | < 500MB |
| 감지 정확도 | > 90% (정면 얼굴) |
| 지원 이미지 크기 | 최대 8K (7680x4320) |

## 📦 단일 실행 파일 빌드

모든 의존성을 포함한 단일 실행 파일 생성:

```bash
# PyInstaller 설치
pip install pyinstaller

# CLI 버전 빌드
python build.py
```

빌드된 실행 파일은 `dist/` 폴더에 생성됩니다:
- Windows: `dist/face-mosaic-local.exe`
- macOS (CLI): `dist/face-mosaic-local`
- Linux: `dist/face-mosaic-local`

## 🍎 macOS 앱 빌드

macOS용 .app 번들 생성 (GUI 포함):

```bash
# macOS 앱 빌드
python build_macos.py
```

빌드된 앱:
- `dist/FaceMosaicLocal.app` - 더블클릭으로 실행 가능한 macOS 앱

### 아이콘 설정

아이콘을 사용하려면:

```bash
# 1. 1024x1024 PNG 아이콘을 assets/icon.png로 저장
# 2. .icns 파일 생성
./create_icon.sh

# 또는 build_macos.py가 자동으로 기본 아이콘 생성
```

### DMG 패키징

앱을 DMG 파일로 패키징:

```bash
python build_macos.py
# DMG 생성 여부를 물어보면 'y' 입력
```

## 🪟 Windows 앱 빌드

Windows용 .exe 실행 파일 생성 (GUI 포함):

```bash
# Windows 앱 빌드
python build_windows.py
```

빌드된 실행 파일:
- `dist/FaceMosaicLocal.exe` - 더블클릭으로 실행 가능한 Windows 실행 파일

### 빌드 전 필수 사항

1. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **모델 파일 다운로드** (DNN 감지기 사용 시):
   ```bash
   python download_models.py
   ```

### 아이콘 설정

아이콘을 사용하려면:

```bash
# 1. 256x256 이상의 PNG 아이콘을 assets/icon.png로 저장
# 2. build_windows.py가 자동으로 .ico 파일로 변환
# 또는 assets/icon.ico 파일을 직접 준비
```

### 빌드 결과물

빌드가 완료되면 `dist/FaceMosaicLocal.exe` 파일이 생성됩니다:
- 모든 의존성과 리소스 파일이 포함된 독립 실행 파일
- 다른 Windows 컴퓨터로 복사하여 바로 실행 가능
- 설치 과정 없이 더블클릭으로 실행

## 🧪 테스트

단위 테스트 실행:

```bash
pytest tests/
```

특정 테스트 파일 실행:

```bash
pytest tests/test_detector.py
```

## 📁 프로젝트 구조

```
face-mosaic-local/
├── src/
│   ├── __init__.py
│   ├── main.py          # CLI 진입점
│   ├── detector.py      # 얼굴 감지 모듈
│   ├── mosaic.py        # 모자이크/블러 처리
│   ├── processor.py     # 일괄 처리 로직
│   ├── utils.py         # 유틸리티 함수
│   └── watermark.py     # 로고/워터마크 추가
├── gui/
│   └── main_window.py   # GUI 메인 윈도우
├── models/              # DNN 모델 파일
├── tests/               # 단위 테스트
├── build/               # 빌드 임시 파일 (gitignore)
├── dist/                # 배포 파일 (gitignore)
├── input/               # 테스트 입력 (gitignore)
├── output/              # 처리 결과 (gitignore)
├── requirements.txt     # 의존성
├── download_models.py   # 모델 다운로드 스크립트
├── build.py             # CLI 빌드 스크립트
├── build_macos.py        # macOS 앱 빌드 스크립트
├── build_windows.py      # Windows 앱 빌드 스크립트
├── pyinstaller.spec      # CLI PyInstaller 설정
├── pyinstaller_macos.spec # macOS 앱 PyInstaller 설정
├── pyinstaller_windows.spec # Windows 앱 PyInstaller 설정
└── README.md             # 이 문서
```

## 🐛 문제 해결

### 모델 파일을 찾을 수 없습니다

DNN 감지기를 사용하려면 모델 파일이 필요합니다:

```bash
python download_models.py
```

### 처리 속도가 느립니다

- Haar Cascade 감지기 사용 (`--detector haar`)
- 이미지 크기 축소 후 처리
- `--mosaic-size` 값을 크게 설정

### 얼굴이 감지되지 않습니다

- DNN 감지기 사용 (`--detector dnn`)
- `--confidence` 값을 낮춤 (예: `0.3`)
- 이미지가 너무 작거나 흐릿한지 확인

## 📝 라이선스

이 프로젝트는 **듀얼 라이선스**를 적용합니다.  
- **무료(Community)**: MIT 라이선스, 배치 5장/회·워터마크 포함  
- **Pro(유료)**: 상용 라이선스, Gumroad에서 구매  
자세한 내용은 [LICENSE](./LICENSE)를 참고하세요.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 📚 참고 자료

- [OpenCV Face Detection](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
- [OpenCV DNN Module](https://docs.opencv.org/4.x/d2/d58/tutorial_table_of_content_dnn.html)
- [DNN Face Detector Model](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)
