# GitHub에 직접 업로드하는 방법

## 방법 1: GitHub CLI 사용 (가장 쉬움)

### 1. GitHub CLI 설치 (없는 경우)

```bash
# macOS
brew install gh

# 또는 공식 설치 스크립트
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
```

### 2. GitHub CLI 로그인

```bash
gh auth login
```

다음 옵션 선택:
- GitHub.com 선택
- HTTPS 또는 SSH 선택
- 브라우저로 인증 또는 토큰 입력

### 3. 저장소 생성 및 푸시

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# GitHub에 저장소 생성 및 푸시 (한 번에!)
gh repo create face-mosaic-local --public --source=. --remote=origin --push
```

또는 단계별로:

```bash
# 저장소 생성
gh repo create face-mosaic-local --public

# 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/face-mosaic-local.git

# 푸시
git push -u origin main
```

---

## 방법 2: Personal Access Token 사용

### 1. GitHub에서 토큰 생성

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" 클릭
3. 권한 선택:
   - `repo` (전체 저장소 권한)
4. 토큰 생성 후 복사 (한 번만 보여줌!)

### 2. 토큰으로 푸시

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# GitHub에서 저장소 먼저 생성 (웹에서)
# 그 다음:

# 원격 저장소 추가 (YOUR_USERNAME과 YOUR_TOKEN 변경)
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/face-mosaic-local.git

# 또는 사용자명과 토큰 분리
git remote add origin https://github.com/YOUR_USERNAME/face-mosaic-local.git
git push -u origin main
# 사용자명: YOUR_USERNAME
# 비밀번호: YOUR_TOKEN
```

---

## 방법 3: SSH 키 사용

### 1. SSH 키 생성 (없는 경우)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 2. SSH 키를 GitHub에 추가

```bash
# 공개 키 복사
cat ~/.ssh/id_ed25519.pub
```

GitHub → Settings → SSH and GPG keys → New SSH key → 복사한 키 붙여넣기

### 3. SSH로 푸시

```bash
cd /Users/st/workspace_ai/face-mosaic-local

# 원격 저장소 추가 (SSH)
git remote add origin git@github.com:YOUR_USERNAME/face-mosaic-local.git

# 푸시
git push -u origin main
```

---

## 자동화 스크립트

다음 스크립트를 실행하면 자동으로 처리합니다:

```bash
#!/bin/bash
cd /Users/st/workspace_ai/face-mosaic-local

# GitHub CLI 사용
if command -v gh &> /dev/null; then
    echo "GitHub CLI 사용 중..."
    gh repo create face-mosaic-local --public --source=. --remote=origin --push
else
    echo "GitHub CLI가 설치되지 않았습니다."
    echo "다음 중 하나를 선택하세요:"
    echo "1. brew install gh (GitHub CLI 설치)"
    echo "2. GITHUB_PUSH.md 파일 참고"
fi
```
