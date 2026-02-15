"""
라이선스 모듈 테스트

유효/무효 키 검증, 배치 제한, 워터마크 on/off, 저장/로드 검증.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.license import LicenseManager


def _make_valid_key(g1: str = "0000", g2: str = "1111", g3: str = "2222") -> str:
    """체크섬이 맞는 키 생성 (테스트용). payload = FMSL+G1+G2+G3 (16자)."""
    payload = f"FMSL{g1}{g2}{g3}"
    checksum = LicenseManager._checksum(payload)
    return f"FMSL-{g1}-{g2}-{g3}-{checksum}"


class TestLicenseValidation:
    """라이선스 키 검증 테스트"""

    def test_valid_key_accepted(self) -> None:
        key = _make_valid_key()
        mgr = LicenseManager()
        assert mgr.validate_key(key) is True

    def test_valid_key_uppercase_normalized(self) -> None:
        key = _make_valid_key().lower()
        mgr = LicenseManager()
        # validate_key 내부에서 strip().upper() 하므로 소문자도 허용
        assert mgr.validate_key(key) is True

    def test_invalid_format_rejected(self) -> None:
        mgr = LicenseManager()
        assert mgr.validate_key("invalid") is False
        assert mgr.validate_key("FMSL-123") is False
        assert mgr.validate_key("FMSL-1234-1234-1234") is False
        assert mgr.validate_key("FMSL-1234-1234-1234-1234-1234") is False
        assert mgr.validate_key("") is False

    def test_wrong_checksum_rejected(self) -> None:
        # 형식은 맞지만 체크섬이 틀린 키
        key = _make_valid_key()
        bad_key = key[:-4] + "0000"
        if bad_key != key:
            mgr = LicenseManager()
            assert mgr.validate_key(bad_key) is False

    def test_g3_tampered_key_rejected(self) -> None:
        """G3 그룹을 변조한 키는 거부되어야 한다."""
        key = _make_valid_key(g1="AAAA", g2="BBBB", g3="CCCC")
        assert LicenseManager().validate_key(key) is True
        parts = key.split("-")
        parts[3] = "ZZZZ"  # G3 변조
        tampered = "-".join(parts)
        assert LicenseManager().validate_key(tampered) is False


class TestBatchLimitAndWatermark:
    """배치 제한 및 워터마크 속성 테스트"""

    def test_free_batch_limit(self) -> None:
        mgr = LicenseManager()
        # 테스트 환경에 .license_key가 없으면 무료 모드
        assert mgr.batch_limit == LicenseManager.FREE_BATCH_LIMIT
        assert mgr.batch_limit == 5

    def test_watermark_enabled_when_free(self) -> None:
        mgr = LicenseManager()
        assert mgr.watermark_enabled is True

    def test_pro_batch_limit_and_no_watermark(self) -> None:
        """Pro 활성화 시 배치 무제한, 워터마크 비활성화."""
        key = _make_valid_key()
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / LicenseManager.CONFIG_DIR_NAME
            config_dir.mkdir(parents=True, exist_ok=True)
            license_file = config_dir / LicenseManager.LICENSE_FILENAME
            license_file.write_text(key, encoding="utf-8")
            with patch.object(Path, "home", return_value=Path(tmp)):
                mgr = LicenseManager()
                assert mgr.is_pro is True
                assert mgr.batch_limit == 0
                assert mgr.watermark_enabled is False


class TestActivateDeactivate:
    """활성화/해제 및 저장·로드 테스트"""

    def test_activate_saves_and_reloads(self) -> None:
        key = _make_valid_key()
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / LicenseManager.CONFIG_DIR_NAME
            with patch.object(Path, "home", return_value=Path(tmp)):
                mgr = LicenseManager()
                assert mgr.activate(key) is True
                assert mgr.is_pro is True
            # 새 인스턴스가 같은 경로에서 읽도록
            with patch.object(Path, "home", return_value=Path(tmp)):
                mgr2 = LicenseManager()
                assert mgr2.is_pro is True

    def test_activate_invalid_key_returns_false(self) -> None:
        mgr = LicenseManager()
        assert mgr.activate("invalid-key") is False
        assert mgr.is_pro is False

    def test_deactivate_clears_license(self) -> None:
        key = _make_valid_key()
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / LicenseManager.CONFIG_DIR_NAME
            config_dir.mkdir(parents=True, exist_ok=True)
            license_file = config_dir / LicenseManager.LICENSE_FILENAME
            license_file.write_text(key, encoding="utf-8")
            with patch.object(Path, "home", return_value=Path(tmp)):
                mgr = LicenseManager()
                assert mgr.is_pro is True
                mgr.deactivate()
                assert mgr.is_pro is False
                assert not license_file.exists()
