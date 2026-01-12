# GitHub 업로드 가이드

## 현재 상태

✅ Git 저장소 초기화 완료
✅ 파일 추가 완료
✅ 초기 커밋 완료

## GitHub에 업로드하는 방법

### 1. GitHub에서 새 저장소 생성

1. https://github.com 에 로그인
2. 우측 상단의 "+" 버튼 클릭 → "New repository" 선택
3. 저장소 정보 입력:
   - Repository name: `face-mosaic-local`
   - Description: `OpenCV 기반 로컬 얼굴 모자이크 처리 프로그램`
   - Public 또는 Private 선택
   - **"Initialize this repository with a README" 체크 해제** (이미 README가 있음)
4. "Create repository" 클릭

### 2. 로컬 저장소와 연결

터미널에서 다음 명령어 실행:

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# GitHub 저장소 URL을 원격 저장소로 추가
# 아래 YOUR_USERNAME을 본인의 GitHub 사용자명으로 변경하세요
git remote add origin https://github.com/YOUR_USERNAME/face-mosaic-local.git

# 또는 SSH 사용 시:
# git remote add origin git@github.com:YOUR_USERNAME/face-mosaic-local.git
```

### 3. GitHub에 푸시

```bash
# 메인 브랜치 이름 확인 (main 또는 master)
git branch

# GitHub에 푸시
git push -u origin main
# 또는 master인 경우:
# git push -u origin master
```

### 4. 완료 확인

GitHub 웹사이트에서 저장소를 확인하세요.

## 빠른 명령어 (한 번에 실행)

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 원격 저장소 추가 (YOUR_USERNAME 변경 필요)
git remote add origin https://github.com/YOUR_USERNAME/face-mosaic-local.git

# 푸시
git push -u origin main
```

## 주의사항

- `.gitignore`에 의해 다음 파일/폴더는 업로드되지 않습니다:
  - `venv/` (가상환경)
  - `build/`, `dist/` (빌드 아티팩트)
  - `input/`, `output/` (테스트 데이터)
  - `*.log` (로그 파일)
  - `models/*.caffemodel` (큰 모델 파일)

- 모델 파일은 별도로 다운로드해야 합니다:
  ```bash
  python download_models.py
  ```

## 추가 작업 (선택사항)

### README 업데이트

GitHub 저장소에 표시될 README.md가 이미 준비되어 있습니다.

### 라이선스 추가

필요시 LICENSE 파일을 추가하세요:
```bash
# MIT 라이선스 예시
cat > LICENSE << 'EOF'
MIT License
Copyright (c) 2026
...
EOF
git add LICENSE
git commit -m "Add LICENSE"
git push
```

### GitHub Actions 설정 (선택)

CI/CD를 위해 GitHub Actions를 설정할 수 있습니다.
