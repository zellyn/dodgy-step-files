"""Smoke tests for the BRL-CAD cross-kernel oracle.

The oracle is install-optional: when `step-g` isn't in PATH, the
oracle reports `not_installed` for every fixture. These tests confirm
the API surface and the graceful-fallback behavior without requiring
BRL-CAD to be present.
"""
from __future__ import annotations

from pathlib import Path

from step_corpus._brlcad_oracle import (
    check_install,
    run_brlcad,
    BRLCAD_BIN,
)


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_FIXTURE = ROOT / "step-examples" / "12-3a-shells" / "Tsh028.stp"


def test_check_install_returns_well_formed_dict() -> None:
    info = check_install()
    assert "installed" in info
    assert "binary" in info
    if info["installed"]:
        assert info["binary"] is not None
        assert info.get("version") is not None
    else:
        assert info["binary"] is None
        assert "reason" in info


def test_run_oracle_on_real_fixture() -> None:
    """Whether or not step-g is installed, the oracle returns the
    canonical 5-field JSON record without raising."""
    assert SAMPLE_FIXTURE.is_file(), "sample fixture missing — corpus invariant"
    result = run_brlcad(SAMPLE_FIXTURE, timeout_s=10)
    assert result["kernel"] == "brlcad"
    assert result["status"] in {"loaded", "rejected", "error", "timeout", "not_installed"}
    assert "n_regions" in result
    assert "stderr_tail" in result
    assert "duration_ms" in result


def test_not_installed_path_is_fast() -> None:
    """When step-g is absent, the oracle should not call subprocess
    and so should return ~instantly."""
    if BRLCAD_BIN is not None:
        # BRL-CAD is installed; this path doesn't apply.
        return
    result = run_brlcad(SAMPLE_FIXTURE, timeout_s=10)
    assert result["status"] == "not_installed"
    assert result["duration_ms"] == 0.0
