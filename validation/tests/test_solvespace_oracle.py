"""Smoke tests for the Solvespace cross-kernel oracle.

The oracle is install-optional: when `solvespace` isn't in PATH, the
oracle reports `not_installed` for every fixture. These tests confirm
the API surface and the graceful-fallback behavior without requiring
solvespace to be present.
"""
from __future__ import annotations

from pathlib import Path

from step_corpus._solvespace_oracle import (
    check_install,
    run_solvespace,
    SOLVESPACE_BIN,
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
    """Whether or not solvespace is installed, the oracle returns the
    canonical 5-field JSON record without raising."""
    assert SAMPLE_FIXTURE.is_file(), "sample fixture missing — corpus invariant"
    result = run_solvespace(SAMPLE_FIXTURE, timeout_s=10)
    assert result["kernel"] == "solvespace"
    assert result["status"] in {"loaded", "rejected", "error", "timeout", "not_installed"}
    assert "n_solids" in result
    assert "stderr_tail" in result
    assert "duration_ms" in result


def test_not_installed_path_is_fast() -> None:
    """When solvespace is absent, the oracle should not call subprocess
    and so should return ~instantly."""
    if SOLVESPACE_BIN is not None:
        # Solvespace is installed; this path doesn't apply.
        return
    result = run_solvespace(SAMPLE_FIXTURE, timeout_s=10)
    assert result["status"] == "not_installed"
    assert result["duration_ms"] == 0.0
