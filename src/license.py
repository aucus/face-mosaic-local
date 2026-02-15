"""
라이선스 키 검증 및 기능 제한 관리 모듈

듀얼 라이선스(무료 제한판 / Pro 유료판) 전환을 위한 오프라인 검증을 제공합니다.
"""

import hashlib
import re
from pathlib import Path
from typing import Optional

# Gumroad URL (상수로 정의, 배포 시 교체 가능)
GUMROAD_URL = "https://gumroad.com/"


class LicenseManager:
    """라이선스 키 검증 및 기능 제한 관리"""

    LICENSE_FILENAME = ".license_key"
    CONFIG_DIR_NAME = ".face-mosaic-local"
    FREE_BATCH_LIMIT = 5
    KEY_PREFIX = "FMSL"
    # 키 형식: FMSL-XXXX-XXXX-XXXX-XXXX (영대문자+숫자, 마지막 4자리 체크섬)
    # FMSL-XXXX-XXXX-XXXX-XXXX (영대문자+숫자 4그룹, 총 20자)
    _KEY_PATTERN = re.compile(
        r"^FMSL-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}$"
    )

    def __init__(self) -> None:
        self.is_pro = False
        self._load_license()

    def _license_file_paths(self) -> list[Path]:
        """검색할 라이선스 파일 경로 목록 (우선순위 순)."""
        home = Path.home()
        config_dir = home / self.CONFIG_DIR_NAME
        # 1) ~/.face-mosaic-local/.license_key
        # 2) 프로젝트 루트(현재 작업 디렉터리) .license_key
        cwd = Path.cwd()
        return [
            config_dir / self.LICENSE_FILENAME,
            cwd / self.LICENSE_FILENAME,
        ]

    def _load_license(self) -> None:
        """저장된 라이선스 키를 로드하고 검증합니다."""
        for path in self._license_file_paths():
            if path.exists() and path.is_file():
                try:
                    key = path.read_text(encoding="utf-8").strip()
                    if key and self.validate_key(key):
                        self.is_pro = True
                        return
                except OSError:
                    continue
        self.is_pro = False

    @staticmethod
    def _checksum(payload: str) -> str:
        """앞 12자리(payload)에 대한 4자리 체크섬 생성 (0-9, A-Z)."""
        # 해시 기반으로 재현 가능한 4자리 생성
        h = hashlib.sha256(payload.encode("utf-8")).digest()
        n = int.from_bytes(h[:4], "big") % (36**4)
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(chars[(n // (36**i)) % 36] for i in range(4))[::-1]

    def validate_key(self, key: str) -> bool:
        """라이선스 키를 검증합니다 (오프라인, 서버 불필요).

        Args:
            key: FMSL-XXXX-XXXX-XXXX-XXXX 형식 문자열

        Returns:
            형식 및 체크섬이 맞으면 True, 아니면 False
        """
        if not key or not isinstance(key, str):
            return False
        key = key.strip().upper()
        if not self._KEY_PATTERN.match(key):
            return False
        parts = key.replace("-", "")
        if len(parts) != 20:  # FMSL(4) + 4그룹(16) = 20
            return False
        payload = parts[:16]  # FMSL + G1 + G2 + G3 (G3 포함하여 변조 방지)
        given_checksum = parts[16:20]  # 마지막 4자리 = G4
        expected = self._checksum(payload)
        return given_checksum == expected

    def activate(self, key: str) -> bool:
        """키를 활성화하고 저장합니다.

        Args:
            key: 라이선스 키

        Returns:
            검증 성공 후 저장 성공 시 True
        """
        if not self.validate_key(key):
            return False
        key = key.strip().upper()
        config_dir = Path.home() / self.CONFIG_DIR_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        license_file = config_dir / self.LICENSE_FILENAME
        try:
            license_file.write_text(key, encoding="utf-8")
            self.is_pro = True
            return True
        except OSError:
            return False

    def deactivate(self) -> None:
        """라이선스를 해제합니다 (저장된 키 파일 삭제)."""
        for path in self._license_file_paths():
            if path.exists() and path.is_file():
                try:
                    path.unlink()
                except OSError:
                    pass
        self.is_pro = False

    @property
    def batch_limit(self) -> int:
        """현재 배치 제한 수. Pro=무제한(0), Free=5."""
        return 0 if self.is_pro else self.FREE_BATCH_LIMIT

    @property
    def watermark_enabled(self) -> bool:
        """무료 버전이면 워터마크 활성화."""
        return not self.is_pro
