"""Smoke tests for the pyvista mesh orientation + quality oracle.

pyvista is already a pymeshfix runtime dep (came in via that wheel),
so the install-optional contract here is "should be importable along
with pymeshfix in any setup that has either installed."
"""
from __future__ import annotations

from pathlib import Path

from step_corpus._pyvista_oracle import (
    check_install,
    run_pyvista,
    _PYVISTA_INSTALLED,
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
    assert SAMPLE_FIXTURE.is_file()
    result = run_pyvista(SAMPLE_FIXTURE)
    assert result["kernel"] == "pyvista"
    assert result["status"] in {"loaded", "rejected", "error", "not_installed"}
    for key in (
        "is_manifold", "n_vertices", "n_triangles",
        "n_orientation_flipped", "max_aspect_ratio",
        "stderr_tail", "duration_ms",
    ):
        assert key in result


def test_loaded_when_installed() -> None:
    """When pyvista is present, Me001 (a known non-manifold fixture)
    should report is_manifold=False."""
    if not _PYVISTA_INSTALLED:
        return
    result = run_pyvista(SAMPLE_FIXTURE)
    assert result["status"] == "loaded", result
    # Me001 is the canonical non-manifold example (3 triangles share an edge).
    assert result["is_manifold"] is False
    assert result["n_vertices"] == 5
    assert result["n_triangles"] == 3
