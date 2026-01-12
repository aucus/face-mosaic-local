#!/bin/bash
# 아이콘 .icns 파일 생성 스크립트

# assets 디렉토리 확인
if [ ! -d "assets" ]; then
    mkdir -p assets
fi

# PNG 아이콘이 있는지 확인
if [ ! -f "assets/icon.png" ]; then
    echo "⚠ assets/icon.png 파일이 없습니다."
    echo "1024x1024 PNG 파일을 assets/icon.png로 저장한 후 다시 실행하세요."
    exit 1
fi

# iconset 디렉토리 생성
ICONSET="assets/icon.iconset"
rm -rf "$ICONSET"
mkdir -p "$ICONSET"

# 다양한 크기의 아이콘 생성
sips -z 16 16     assets/icon.png --out "$ICONSET/icon_16x16.png"
sips -z 32 32     assets/icon.png --out "$ICONSET/icon_16x16@2x.png"
sips -z 32 32     assets/icon.png --out "$ICONSET/icon_32x32.png"
sips -z 64 64     assets/icon.png --out "$ICONSET/icon_32x32@2x.png"
sips -z 128 128   assets/icon.png --out "$ICONSET/icon_128x128.png"
sips -z 256 256   assets/icon.png --out "$ICONSET/icon_128x128@2x.png"
sips -z 256 256   assets/icon.png --out "$ICONSET/icon_256x256.png"
sips -z 512 512   assets/icon.png --out "$ICONSET/icon_256x256@2x.png"
sips -z 512 512   assets/icon.png --out "$ICONSET/icon_512x512.png"
sips -z 1024 1024 assets/icon.png --out "$ICONSET/icon_512x512@2x.png"

# .icns 파일 생성
iconutil -c icns "$ICONSET" -o assets/icon.icns

# 임시 iconset 디렉토리 삭제
rm -rf "$ICONSET"

echo "✓ 아이콘 생성 완료: assets/icon.icns"
