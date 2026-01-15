# Face Mosaic Local - Tasks

> 📍 위치: `/Users/st/workspace_ai/face-mosaic-local`  
> 📅 생성일: 2026-01-12  
> 🎯 목표: OpenCV 기반 로컬 얼굴 모자이크 프로그램 구현

---

## Phase 1: 프로젝트 설정 ⏱️ 30분

### 1.1 환경 구성
- [x] Python 가상환경 생성 (`python -m venv venv`)
- [ ] 가상환경 활성화
- [x] requirements.txt 생성
- [ ] 의존성 설치 (`pip install -r requirements.txt`)

### 1.2 프로젝트 구조 생성
- [x] `src/` 디렉토리 생성
- [x] `src/__init__.py` 생성
- [x] `models/` 디렉토리 생성
- [x] `tests/` 디렉토리 생성
- [x] `input/` 디렉토리 생성 (테스트용)
- [x] `output/` 디렉토리 생성
- [x] `.gitignore` 생성

### 1.3 DNN 모델 다운로드
- [x] `deploy.prototxt` 다운로드 (스크립트 생성)
- [x] `res10_300x300_ssd_iter_140000.caffemodel` 다운로드 (스크립트 생성)
- [x] 모델 파일 `models/` 폴더에 배치 (스크립트 생성)
- [ ] 모델 로드 테스트

---

## Phase 2: 얼굴 감지 모듈 ⏱️ 1시간

### 2.1 기본 감지기 구현 (`src/detector.py`)
- [x] `FaceDetector` 베이스 클래스 정의
- [x] `detect(image)` 메서드 인터페이스 정의
- [x] 반환 형식 정의: `List[BoundingBox]`

### 2.2 Haar Cascade 감지기
- [x] `HaarCascadeDetector` 클래스 구현
- [x] OpenCV 내장 cascade 파일 로드
- [x] `detectMultiScale` 파라미터 튜닝
- [ ] 단일 이미지 테스트

### 2.3 DNN 감지기 (권장)
- [x] `DNNDetector` 클래스 구현
- [x] 모델 로드 (`cv2.dnn.readNetFromCaffe`)
- [x] blob 전처리 구현
- [x] confidence threshold 적용
- [ ] 단일 이미지 테스트

### 2.4 감지기 팩토리
- [x] `get_detector(type)` 팩토리 함수 구현
- [x] 타입별 감지기 인스턴스 반환
- [x] 기본값 설정 (dnn)

---

## Phase 3: 모자이크 처리 모듈 ⏱️ 30분

### 3.1 모자이크 함수 구현 (`src/mosaic.py`)
- [x] `apply_mosaic(image, bbox, block_size)` 함수 구현
- [x] 영역 추출 → 축소 → 확대 로직
- [x] 경계 처리 (이미지 범위 벗어나는 경우)

### 3.2 블러 함수 구현
- [x] `apply_blur(image, bbox, kernel_size)` 함수 구현
- [x] Gaussian blur 적용
- [x] 커널 크기 유효성 검사

### 3.3 통합 함수
- [x] `process_faces(image, bboxes, method, **kwargs)` 구현
- [x] method 파라미터: 'mosaic' | 'blur'
- [x] 다중 얼굴 순차 처리

---

## Phase 4: 유틸리티 모듈 ⏱️ 20분

### 4.1 파일 유틸리티 (`src/utils.py`)
- [x] `get_image_files(folder)` 함수 구현
- [x] 지원 확장자 필터링 (jpg, png, etc.)
- [x] 재귀 탐색 옵션

### 4.2 이미지 I/O
- [x] `load_image(path)` 함수 구현
- [x] `save_image(image, path, quality)` 함수 구현
- [x] EXIF 메타데이터 보존 처리

### 4.3 로깅 설정
- [x] 로거 설정 함수 구현
- [x] 파일 + 콘솔 핸들러 설정
- [x] 로그 포맷 정의

---

## Phase 5: 일괄 처리 모듈 ⏱️ 1시간

### 5.1 프로세서 클래스 (`src/processor.py`)
- [x] `FaceMosaicProcessor` 클래스 정의
- [x] 생성자: detector, mosaic 설정 받기
- [x] `process_image(input_path, output_path)` 메서드

### 5.2 폴더 처리
- [x] `process_folder(input_dir, output_dir)` 메서드
- [x] tqdm 진행률 표시
- [x] 에러 발생 시 스킵 & 로깅

### 5.3 결과 리포트
- [x] 처리 통계 수집 (성공/실패/스킵)
- [x] 감지된 얼굴 수 집계
- [x] 처리 시간 측정
- [x] 최종 리포트 출력

---

## Phase 6: CLI 인터페이스 ⏱️ 40분

### 6.1 argparse 설정 (`src/main.py`)
- [x] `--input` 필수 인자 정의
- [x] `--output` 선택 인자 (기본값: ./output)
- [x] `--detector` 선택 인자 (haar/dnn)
- [x] `--mosaic-size` 선택 인자 (기본값: 15)
- [x] `--method` 선택 인자 (mosaic/blur)
- [x] `--confidence` 선택 인자 (기본값: 0.5)

### 6.2 실행 로직
- [x] 인자 파싱 및 유효성 검사
- [x] 프로세서 인스턴스 생성
- [x] 처리 실행
- [x] 결과 출력

### 6.3 에러 핸들링
- [x] 입력 폴더 존재 확인
- [x] 출력 폴더 자동 생성
- [x] 모델 파일 존재 확인
- [x] 친절한 에러 메시지

---

## Phase 7: 테스트 ⏱️ 40분

### 7.1 단위 테스트 작성
- [x] `tests/test_detector.py` 작성
- [x] `tests/test_mosaic.py` 작성
- [x] `tests/test_processor.py` 작성

### 7.2 통합 테스트
- [ ] 샘플 이미지로 E2E 테스트 (수동 테스트 필요)
- [ ] 다양한 케이스 테스트:
  - [ ] 얼굴 없는 이미지
  - [ ] 다중 얼굴 이미지
  - [ ] 큰 이미지 (4K+)
  - [ ] 회전된 이미지

### 7.3 성능 테스트
- [ ] 100장 이미지 배치 테스트 (수동 테스트 필요)
- [ ] 처리 시간 측정
- [ ] 메모리 사용량 확인

---

## Phase 8: 문서화 ⏱️ 30분

### 8.1 README.md 작성
- [x] 프로젝트 소개
- [x] 설치 방법
- [x] 사용법 (CLI 예시)
- [x] 옵션 설명
- [x] 라이선스

### 8.2 코드 문서화
- [x] 모든 public 함수에 docstring
- [x] 타입 힌트 추가
- [x] 인라인 주석 (복잡한 로직)

---

## 🎉 완료 체크리스트

### MVP (최소 기능)
- [x] 단일 이미지 얼굴 모자이크 ✅
- [x] 폴더 일괄 처리 ✅
- [x] CLI 실행 가능 ✅
- [x] 기본 로깅 ✅

### v1.0 (안정 버전)
- [x] MVP 완료
- [x] 두 가지 감지 방식 (Haar, DNN)
- [x] 모자이크/블러 선택
- [x] 단위 테스트 통과
- [x] README 완성

### 추가 기능 (Optional)
- [ ] GUI 인터페이스
- [ ] 미리보기 기능
- [ ] 특정 얼굴 제외 기능
- [ ] 배치 처리 최적화 (멀티스레딩)

### v1.1 기능 (로고 추가)
- [x] 로고 추가 모듈 구현
- [x] 우측 하단 위치 배치
- [x] 로고 크기/투명도/여백 조절
- [x] CLI 옵션 추가
- [x] 단위 테스트 작성

### v1.2 기능 (단일 실행 프로그램)
- [x] PyInstaller 설정
- [x] 빌드 스크립트 작성
- [x] 의존성 포함 확인
- [ ] 플랫폼별 빌드 (실제 빌드 테스트 필요)
- [ ] 배포 패키지 생성

### v1.3 기능 (GUI 인터페이스)
- [x] GUI 메인 윈도우
- [x] 폴더 선택 기능
- [x] 옵션 설정 UI
- [x] 진행 상황 표시
- [x] 로그 출력 영역
- [x] 에러 핸들링

### v1.4 기능 (macOS 앱 빌드)
- [x] macOS .app 번들 생성
- [x] 앱 아이콘 설정
- [x] Info.plist 설정
- [x] GUI 모드 설정
- [x] DMG 패키징 스크립트 작성
- [ ] 코드 서명 (선택, 개발자 인증서 필요)

### v1.5 기능 (수동 모자이크 지정)
- [x] 수동 모자이크 GUI 창 구현
- [x] 마우스 드래그 영역 선택
- [x] 여러 영역 선택 및 관리
- [x] 모자이크 크기 조절
- [x] 이미지 네비게이션
- [x] 저장 기능

---

## Phase 9: 로고 추가 기능 ⏱️ 1시간

### 9.1 워터마크 모듈 구현 (`src/watermark.py`)
- [x] `add_logo()` 함수 구현
- [x] 로고 이미지 로드 (PNG 알파 채널 지원)
- [x] 우측 하단 위치 계산
- [x] 로고 크기 조절 (비율 또는 절대 크기)
- [x] 투명도 처리 (알파 블렌딩)
- [x] 여백(margin) 적용

### 9.2 프로세서 통합
- [x] `FaceMosaicProcessor`에 로고 옵션 추가
- [x] `process_image()` 메서드에 로고 추가 로직 통합
- [x] 로고 파일 존재 확인 및 에러 핸들링

### 9.3 CLI 옵션 추가
- [x] `--logo` 옵션 추가 (로고 파일 경로)
- [x] `--logo-size` 옵션 추가 (크기 비율, 기본값: 0.1)
- [x] `--logo-margin` 옵션 추가 (여백 픽셀, 기본값: 20)
- [x] `--logo-opacity` 옵션 추가 (투명도, 기본값: 1.0)

### 9.4 테스트
- [x] `tests/test_watermark.py` 작성
- [x] 로고 추가 단위 테스트
- [x] 다양한 로고 크기/위치 테스트
- [x] 투명도 처리 테스트

---

## Phase 10: 단일 실행 프로그램 빌드 ⏱️ 2시간

### 10.1 PyInstaller 설정
- [x] `pyinstaller.spec` 파일 작성
- [x] 의존성 패키지 포함 설정
- [x] DNN 모델 파일 포함 설정
- [ ] 아이콘 파일 설정 (선택)
- [x] 단일 파일/폴더 모드 선택

### 10.2 빌드 스크립트 작성
- [x] `build.py` 또는 `build.sh` 작성
- [x] 플랫폼별 빌드 명령어
- [x] 빌드 전 정리 작업
- [x] 빌드 후 검증

### 10.3 의존성 확인
- [x] 모든 Python 패키지 포함 확인
- [ ] OpenCV DLL/라이브러리 포함 확인 (실제 빌드 시 테스트 필요)
- [ ] NumPy, Pillow 등 포함 확인 (실제 빌드 시 테스트 필요)
- [x] DNN 모델 파일 경로 확인

### 10.4 테스트 및 배포
- [ ] 실행 파일 테스트 (다른 PC에서)
- [ ] 파일 크기 최적화
- [ ] 배포 패키지 생성
- [ ] 사용 가이드 작성

---

## Phase 11: GUI 인터페이스 구현 ⏱️ 3시간

### 11.1 GUI 메인 윈도우 (`gui/main_window.py`)
- [x] tkinter 기반 메인 윈도우 생성
- [x] 윈도우 레이아웃 설계
- [x] 제목 및 기본 정보 표시
- [x] 윈도우 크기 및 위치 설정

### 11.2 폴더 선택 기능
- [x] 입력 폴더 선택 버튼 및 다이얼로그
- [x] 출력 폴더 선택 버튼 및 다이얼로그
- [x] 선택된 경로 표시
- [x] 경로 유효성 검사

### 11.3 옵션 설정 UI
- [x] 감지기 선택 (Haar/DNN 라디오 버튼)
- [x] 처리 방법 선택 (모자이크/블러 라디오 버튼)
- [x] 모자이크 크기 슬라이더 (1-50)
- [x] 신뢰도 슬라이더 (0.1-1.0)
- [x] 로고 파일 선택 버튼
- [x] 로고 옵션 (크기, 여백, 투명도) 입력 필드

### 11.4 진행 상황 표시
- [x] 프로그레스 바 위젯
- [x] 처리 중 상태 표시
- [x] 현재 처리 중인 파일 표시
- [x] 완료/실패 통계 표시

### 11.5 로그 출력 영역
- [x] 텍스트 위젯 또는 스크롤 가능한 로그 영역
- [x] 실시간 로그 출력
- [ ] 로그 레벨별 색상 구분 (선택)
- [ ] 로그 저장 기능 (선택)

### 11.6 처리 로직 통합
- [x] "처리 시작" 버튼 이벤트
- [x] 백그라운드 스레드에서 처리 실행
- [x] GUI 스레드 블로킹 방지
- [x] 처리 완료 후 결과 표시

### 11.7 에러 핸들링
- [x] 에러 메시지 다이얼로그
- [x] 친절한 에러 안내
- [x] 처리 중단 기능
- [x] 예외 처리

### 11.8 GUI 테스트
- [ ] 각 기능별 테스트 (수동 테스트 필요)
- [ ] 다양한 옵션 조합 테스트
- [ ] 에러 상황 테스트
- [ ] 사용성 테스트

---

## Phase 12: macOS 앱 빌드 ⏱️ 1.5시간

### 12.1 macOS .app 번들 생성
- [x] PyInstaller macOS 앱 설정 (`pyinstaller_macos.spec`)
- [x] `console=False` 옵션으로 GUI 모드 설정
- [x] .app 번들 구조 확인
- [x] 실행 파일 경로 설정

### 12.2 앱 아이콘 설정
- [x] .icns 파일 생성 스크립트 작성 (`create_icon.sh`)
- [x] 기본 아이콘 생성 기능 (`build_macos.py`)
- [x] PyInstaller spec에 아이콘 경로 추가
- [ ] 아이콘 적용 확인 (실제 빌드 시 테스트 필요)

### 12.3 Info.plist 설정
- [x] CFBundleName 설정
- [x] CFBundleIdentifier 설정
- [x] CFBundleVersion 설정
- [x] NSHighResolutionCapable 설정 (Retina 지원)
- [x] 필요한 권한 설정 (파일 접근 등)

### 12.4 GUI 모드 설정
- [x] `console=False` 옵션 적용
- [x] GUI 진입점 설정 (gui/main_window.py)
- [x] CLI 모드와 분리

### 12.5 DMG 패키징 (선택)
- [x] DMG 생성 스크립트 작성 (`build_macos.py`)
- [x] 앱을 Applications 폴더로 드래그 안내
- [ ] DMG 배경 이미지 설정 (선택)
- [ ] DMG 파일 생성 (실제 빌드 시 테스트 필요)

### 12.6 코드 서명 (선택)
- [ ] 개발자 인증서 준비
- [ ] 코드 서명 스크립트 작성
- [ ] 공증 (notarization) 설정 (선택)
- [ ] 서명 확인

### 12.7 테스트
- [ ] .app 번들 실행 테스트 (실제 빌드 후)
- [ ] 다른 Mac에서 테스트
- [ ] 권한 문제 확인
- [ ] 파일 경로 문제 확인

---

## Phase 13: 수동 모자이크 지정 기능 ⏱️ 2.5시간

### 13.1 수동 모자이크 GUI 창 구현 (`gui/manual_mosaic_window.py`)
- [x] 메인 윈도우 클래스 생성 (`ManualMosaicWindow`)
- [x] input 폴더 선택 기능
- [x] 이미지 목록 표시 및 선택
- [x] 이미지 표시 영역 (커스텀 ImageLabel)
- [x] 이미지 크기 조절 (fit to window)

### 13.2 마우스 드래그 영역 선택
- [x] 마우스 이벤트 처리 (mousePressEvent, mouseMoveEvent, mouseReleaseEvent)
- [x] 드래그 시작점 및 종료점 추적
- [x] 드래그 중 사각형 미리보기 표시
- [x] 선택된 영역 좌표 계산 (x, y, width, height)

### 13.3 선택된 영역 관리
- [x] 선택된 영역 리스트 저장
- [x] 선택된 영역 시각적 표시 (사각형 그리기)
- [x] 영역 삭제 기능 (우클릭)
- [x] 모든 영역 초기화 기능

### 13.4 모자이크 처리 및 저장
- [x] 모자이크 크기 슬라이더 (1-50)
- [ ] 실시간 모자이크 미리보기 (선택사항, 미구현)
- [x] 선택된 영역에 모자이크 적용
- [x] 처리된 이미지 저장 (output 폴더)
- [x] 원본 파일명 유지

### 13.5 이미지 네비게이션
- [x] 이전 이미지 버튼
- [x] 다음 이미지 버튼
- [x] 현재 이미지 인덱스 표시 (예: 1/10)
- [x] 이미지 변경 시 선택 영역 초기화

### 13.6 UI 구성
- [x] 폴더 선택 버튼
- [x] 이미지 표시 영역
- [x] 모자이크 크기 조절 슬라이더
- [x] 영역 관리 버튼 (초기화)
- [x] 저장 버튼
- [x] 이미지 네비게이션 버튼
- [x] 상태 표시 (현재 이미지, 출력 폴더)

### 13.7 기존 GUI 통합
- [x] 메인 GUI에 "수동 모자이크 지정" 버튼 추가
- [x] 수동 모자이크 창 열기 기능
- [x] 입력/출력 폴더 자동 전달
- [x] 두 모드 간 전환 가능

### 13.8 테스트
- [ ] 마우스 드래그 영역 선택 테스트 (수동 테스트 필요)
- [ ] 여러 영역 선택 테스트 (수동 테스트 필요)
- [ ] 모자이크 적용 테스트 (수동 테스트 필요)
- [ ] 저장 기능 테스트 (수동 테스트 필요)
- [ ] 이미지 네비게이션 테스트 (수동 테스트 필요)

---

## 📝 진행 노트

### 2026-01-12
- PRD.md, Tasks.md 초안 작성
- 프로젝트 폴더 생성
- Phase 1-8 전체 구현 완료
  - 프로젝트 구조 및 환경 설정
  - 얼굴 감지 모듈 (Haar Cascade, DNN)
  - 모자이크/블러 처리 모듈
  - 유틸리티 모듈 (파일 I/O, 로깅)
  - 일괄 처리 모듈
  - CLI 인터페이스
  - 단위 테스트
  - README.md 문서화
- 로고 추가 기능 요구사항 문서화 (FR-008)
  - PRD.md에 기능 요구사항 추가
  - Tasks.md에 Phase 9 작업 항목 추가
- Phase 9: 로고 추가 기능 구현 완료
  - `src/watermark.py` 모듈 구현
  - 프로세서에 로고 기능 통합
  - CLI 옵션 추가 (`--logo`, `--logo-size`, `--logo-margin`, `--logo-opacity`)
  - 단위 테스트 작성 및 통과 (35개 테스트 모두 통과)
- 단일 실행 프로그램 및 GUI 인터페이스 요구사항 문서화
  - PRD.md에 FR-009 (단일 실행 프로그램), FR-010 (GUI 인터페이스) 추가
  - Tasks.md에 Phase 10 (단일 실행 프로그램), Phase 11 (GUI 인터페이스) 추가
- Phase 10: 단일 실행 프로그램 빌드 구현 완료
  - `pyinstaller.spec` 파일 작성
  - `build.py` 빌드 스크립트 작성
  - 의존성 포함 설정 완료
- Phase 11: GUI 인터페이스 구현 완료
  - `gui/main_window.py` 구현
  - tkinter 기반 직관적인 UI 구성
  - 모든 옵션 설정 기능 포함
  - 백그라운드 처리 및 실시간 로그 표시
- macOS 앱 빌드 요구사항 문서화
  - PRD.md에 v1.4 완료 조건 추가
  - Tasks.md에 Phase 12 (macOS 앱 빌드) 추가
- Phase 12: macOS 앱 빌드 구현 완료
  - `pyinstaller_macos.spec` 파일 작성 (GUI 모드, Info.plist 포함)
  - `build_macos.py` 빌드 스크립트 작성
  - `create_icon.sh` 아이콘 생성 스크립트 작성
  - DMG 패키징 기능 포함
  - 앱 번들 생성 성공 (69MB)
- 수동 모자이크 지정 기능 요구사항 문서화 (FR-012)
  - PRD.md에 기능 요구사항 추가
  - Tasks.md에 Phase 13 작업 항목 추가
- Phase 13: 수동 모자이크 지정 기능 구현 완료
  - `gui/manual_mosaic_window.py` 구현
  - 커스텀 ImageLabel 위젯 (마우스 드래그 영역 선택)
  - 여러 영역 선택 및 관리
  - 모자이크 크기 조절 슬라이더
  - 이미지 네비게이션 (이전/다음)
  - 처리된 이미지 저장 기능
  - 기존 GUI에 "수동 모자이크 지정" 버튼 추가 및 통합

---

## 🔗 참고 자료

- [OpenCV Face Detection](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
- [OpenCV DNN Module](https://docs.opencv.org/4.x/d2/d58/tutorial_table_of_content_dnn.html)
- [DNN Face Detector Model](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)
