# 프로그램 실행 방법

## ✅ GUI 실행 (PySide6 사용)

**PySide6 기반 GUI로 재구현되었습니다!**

tkinter 대신 PySide6를 사용하여 macOS 26.2 호환성 문제를 해결했습니다.
st_ocr 프로젝트와 동일한 방식으로 구현되었습니다.

## 🚀 GUI 실행 방법

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 가상환경 활성화 (있는 경우)
source venv/bin/activate

# PySide6 설치 (처음 한 번만)
pip install PySide6

# GUI 실행
python -m gui.main_window

# 또는 실행 스크립트 사용
./run_gui_pyside6.sh
```

## 📝 CLI 사용 (대안)

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 방법 1: 실행 스크립트 사용 (가장 쉬움)
./run_cli.sh

# 방법 2: 기본 실행
python -m src.main --input ./input --output ./output

# 방법 3: 옵션 지정
python -m src.main \
  --input ./input \
  --output ./output \
  --detector dnn \
  --mosaic-size 10 \
  --confidence 0.3

# 방법 4: 가상환경 사용
source venv/bin/activate
python -m src.main --input ./input --output ./output
```

## 💡 GUI 기능

- ✅ 폴더 선택 (입력/출력)
- ✅ 감지기 선택 (Haar/DNN)
- ✅ 처리 방법 선택 (모자이크/블러)
- ✅ 모자이크 크기 조절 (슬라이더)
- ✅ 신뢰도 조절 (슬라이더)
- ✅ 로고 추가 옵션
- ✅ 실시간 진행 상황 표시
- ✅ 로그 출력
- ✅ 백그라운드 처리 (GUI 블로킹 없음)

## 📝 빠른 테스트

CLI로 바로 테스트:

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 실행 스크립트 사용 (가장 쉬움)
./run_cli.sh

# 또는 직접 실행
python -m src.main --input ./input --output ./output --detector dnn --mosaic-size 10
```

결과는 `./output` 폴더에 저장됩니다.

## 💡 CLI 사용 팁

### 로고 추가
```bash
python -m src.main \
  --input ./input \
  --output ./output \
  --logo ./logo/test_logo.png \
  --logo-size 0.15 \
  --logo-margin 30
```

### 블러 사용
```bash
python -m src.main \
  --input ./input \
  --output ./output \
  --method blur
```

### Haar Cascade 사용 (더 빠름, 정확도 낮음)
```bash
python -m src.main \
  --input ./input \
  --output ./output \
  --detector haar
```
