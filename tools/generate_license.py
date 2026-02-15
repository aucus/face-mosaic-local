#!/usr/bin/env python3
"""
라이선스 키 생성 유틸리티

Gumroad 판매 시 수동으로 키를 생성해 제공할 때 사용합니다.
형식: FMSL-XXXX-XXXX-XXXX-XXXX (영대문자+숫자, 마지막 4자리 체크섬)
"""

import argparse
import random
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.license import LicenseManager

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_one() -> str:
    """체크섬이 맞는 라이선스 키 한 개 생성 (FMSL-G1-G2-G3-체크섬)."""
    part1 = "".join(random.choices(CHARS, k=4))
    part2 = "".join(random.choices(CHARS, k=4))
    part3 = "".join(random.choices(CHARS, k=4))
    payload = f"FMSL{part1}{part2}{part3}"  # FMSL+G1+G2+G3 (16자) 기준 체크섬
    checksum = LicenseManager._checksum(payload)
    return f"FMSL-{part1}-{part2}-{part3}-{checksum}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Face Mosaic Local 라이선스 키 생성 (FMSL-XXXX-XXXX-XXXX-XXXX)"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="생성할 키 개수 (기본값: 1)",
    )
    args = parser.parse_args()
    if args.count < 1 or args.count > 1000:
        print("오류: 개수는 1~1000 사이로 지정하세요.", file=sys.stderr)
        return 1
    mgr = LicenseManager()
    for _ in range(args.count):
        key = generate_one()
        if mgr.validate_key(key):
            print(key)
        else:
            print(f"검증 실패: {key}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
