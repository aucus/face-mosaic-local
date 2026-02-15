# Face Mosaic Local — 문서 및 랜딩

이 폴더는 **GitHub Pages** 배포용입니다.

## Pages가 안 열릴 때 체크

1. **저장소 설정**: GitHub → 해당 repo → **Settings** → **Pages**
2. **Source**: "Deploy from a branch"
3. **Branch**: `main` (또는 사용 중인 기본 브랜치)
4. **Folder**: **`/docs`** 로 설정되어 있어야 합니다. (root가 아님)
5. 저장 후 2~5분 기다린 뒤 `https://aucus.github.io/face-mosaic-local/` 접속
6. **Branch가 `main`이 아니라면** (예: `master`) Branch를 실제 기본 브랜치로 맞추기

`/ (root)`로 두면 이 폴더가 아닌 프로젝트 루트가 배포되므로, **반드시 Folder를 `/docs`로 선택**해야 합니다.

## 로컬에서 확인

```bash
cd docs
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000
```
