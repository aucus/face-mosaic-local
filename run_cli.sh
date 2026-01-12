#!/bin/bash
# CLI 실행 스크립트 (GUI 문제 해결용)

cd "$(dirname "$0")"

# 기본값 설정
INPUT_DIR="${1:-./input}"
OUTPUT_DIR="${2:-./output}"
DETECTOR="${3:-dnn}"
MOSAIC_SIZE="${4:-10}"
CONFIDENCE="${5:-0.3}"

echo "=========================================="
echo "Face Mosaic Local - CLI 실행"
echo "=========================================="
echo "입력 폴더: $INPUT_DIR"
echo "출력 폴더: $OUTPUT_DIR"
echo "감지기: $DETECTOR"
echo "모자이크 크기: $MOSAIC_SIZE"
echo "신뢰도: $CONFIDENCE"
echo "=========================================="
echo ""

# Python 실행
if [ -d "venv" ]; then
    echo "가상환경 사용..."
    source venv/bin/activate
    python -m src.main \
        --input "$INPUT_DIR" \
        --output "$OUTPUT_DIR" \
        --detector "$DETECTOR" \
        --mosaic-size "$MOSAIC_SIZE" \
        --confidence "$CONFIDENCE"
else
    echo "시스템 Python 사용..."
    python3 -m src.main \
        --input "$INPUT_DIR" \
        --output "$OUTPUT_DIR" \
        --detector "$DETECTOR" \
        --mosaic-size "$MOSAIC_SIZE" \
        --confidence "$CONFIDENCE"
fi
