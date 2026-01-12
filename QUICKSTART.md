# Face Mosaic Local - 빠른 시작 가이드

## 🚀 빠른 실행

### GUI 실행 (추천)

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 가상환경 활성화 (있는 경우)
source venv/bin/activate

# PySide6 설치 (처음 한 번만)
pip install PySide6

# GUI 실행
python -m gui.main_window
```

**GUI 사용 순서:**
1. 입력 폴더 선택 → 이미지가 있는 폴더 선택
2. 출력 폴더 선택 → 결과 저장 폴더 선택
3. 옵션 설정 (감지기, 처리 방법, 모자이크 크기 등)
4. "처리 시작" 버튼 클릭
5. 진행 상황 확인

---

### CLI 실행

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 기본 실행
python -m src.main --input ./input --output ./output

# 옵션 지정
python -m src.main \
  --input ./input \
  --output ./output \
  --detector dnn \
  --mosaic-size 10 \
  --confidence 0.3

# 로고 추가
python -m src.main \
  --input ./input \
  --output ./output \
  --logo ./logo/test_logo.png \
  --logo-size 0.15
```

---

## 📋 필수 준비사항

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. DNN 모델 다운로드 (선택사항)

DNN 감지기를 사용하려면:

```bash
python download_models.py
```

---

## ⚠️ 문제 해결

### GUI가 실행되지 않는 경우

1. **PySide6 설치 확인**
   ```bash
   pip install PySide6
   ```

2. **의존성 확인**
   ```bash
   python -c "import cv2, numpy, PIL, tqdm, PySide6; print('✓ 모든 의존성 설치됨')"
   ```

### CLI 실행 시 오류

1. **모델 파일 확인**
   ```bash
   ls models/  # deploy.prototxt와 res10_300x300_ssd_iter_140000.caffemodel 확인
   python download_models.py  # 없으면 다운로드
   ```

2. **입력 폴더 확인**
   ```bash
   ls input/  # 이미지 파일이 있는지 확인
   ```

---

## 💡 사용 팁

- **처음 사용**: GUI 사용 권장
- **배치 처리**: CLI가 더 빠름
- **로고 추가**: GUI에서도 로고 파일 선택 가능
