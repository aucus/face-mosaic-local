#!/bin/bash
# PySide6 GUI 실행 스크립트

cd "$(dirname "$0")"

# 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    echo "가상환경 활성화..."
    source venv/bin/activate
fi

# PySide6 설치 확인
python -c "import PySide6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PySide6가 설치되지 않았습니다. 설치 중..."
    pip install PySide6
fi

# GUI 실행
python -m gui.main_window
