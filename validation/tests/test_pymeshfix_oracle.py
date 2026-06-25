"""Smoke tests for the pymeshfix mesh oracle.

Unlike the binary-subprocess oracles (brlcad, solvespace), pymeshfix is
a Python package, so the install check is `try: import pymeshfix`.
Tests confirm the API surface and graceful fallback when pymeshfix
isn't installed.
"""
from __future__ import annotations

from pathlib import Path

from step_corpus._pymeshfix_oracle import (
    check_install,
    run_pymeshfix,
    _PYMESHFIX_INSTALLED,
)


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_FIXTURE = ROOT / "mesh-examples" / "12-14-mesh" / "Me001.mesh.json"


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
    """Oracle returns the canonical record shape regardless of install state."""
    assert SAMPLE_FIXTURE.is_file(), "sample mesh fixture missing — corpus invariant"
    result = run_pymeshfix(SAMPLE_FIXTURE)
    assert result["kernel"] == "pymeshfix"
    assert result["status"] in {"loaded", "rejected", "error", "not_installed"}
    for key in (
        "n_vertices_in", "n_triangles_in", "n_vertices_out", "n_triangles_out",
        "n_boundaries", "stderr_tail", "duration_ms",
    ):
        assert key in result


def test_not_installed_path_is_fast() -> None:
    """When pymeshfix is absent, the oracle returns instantly."""
    if _PYMESHFIX_INSTALLED:
        return
    result = run_pymeshfix(SAMPLE_FIXTURE)
    assert result["status"] == "not_installed"
    assert result["duration_ms"] == 0.0


def test_loaded_when_installed() -> None:
    """When pymeshfix is present, a real fixture should produce a "loaded"
    record with non-null vertex/triangle counts."""
    if not _PYMESHFIX_INSTALLED:
        return
    result = run_pymeshfix(SAMPLE_FIXTURE)
    assert result["status"] == "loaded", result
    assert result["n_vertices_in"] is not None and result["n_vertices_in"] > 0
    assert result["n_triangles_in"] is not None and result["n_triangles_in"] > 0
    # Output counts may legitimately be 0 (e.g. fixture too defective to repair)
    assert result["n_vertices_out"] is not None
    assert result["n_triangles_out"] is not None
