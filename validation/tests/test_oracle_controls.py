"""Negative-control tests: oracle pipeline returns CLEAN on known-good input.

These controls live outside the catalog (step-controls/ and mesh-controls/)
and are named with the Ctl prefix so they are obviously distinct from catalog
fixtures (Le*, Tsh*, etc.).  They must NOT appear in STEP_PROBLEM_CATALOG.md
and are NOT enumerated by catalog.iter_canonical().

Oracles exercised:
  - validate2 (occt_heal_on, occt_heal_off, part21_strict) for STEP controls
  - _schema_oracle.check_fixture() for STEP controls
  - _mesh_oracle.check_one() for mesh controls

Run independently (not wired into main CI by default)::

    cd validation && uv run pytest tests/test_oracle_controls.py -v

If any test fails, the oracle pipeline has regressed in a way that would
over-report defects on valid STEP files or meshes.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────────

_VALIDATION = Path(__file__).resolve().parent.parent
_REPO = _VALIDATION.parent
_STEP_CONTROLS = _REPO / "step-controls"
_MESH_CONTROLS = _REPO / "mesh-controls"


# ── Fixture discovery ──────────────────────────────────────────────────────────

def _discover_step_controls() -> list[Path]:
    """Discover all Ctl*.stp files under step-controls/."""
    return sorted(_STEP_CONTROLS.rglob("Ctl*.stp"))


def _discover_mesh_controls() -> list[Path]:
    """Discover all Ctl*.mesh.json files under mesh-controls/."""
    return sorted(_MESH_CONTROLS.rglob("Ctl*.mesh.json"))


_STEP_PATHS = _discover_step_controls()
_MESH_PATHS = _discover_mesh_controls()

_STEP_IDS = [p.stem for p in _STEP_PATHS]
_MESH_IDS = [p.stem.replace(".mesh", "") for p in _MESH_PATHS]


# ── Catalog non-membership check ───────────────────────────────────────────────

def test_controls_not_in_catalog() -> None:
    """Control IDs must not appear in the canonical catalog."""
    from step_corpus import catalog
    catalog_ids = {e["id"] for e in catalog.iter_canonical()}
    ctl_ids = set(_STEP_IDS) | {p.stem.replace(".mesh", "") for p in _MESH_PATHS}
    overlap = ctl_ids & catalog_ids
    assert not overlap, (
        f"Control IDs found in catalog (they must not be!): {sorted(overlap)}"
    )


def test_controls_have_ctl_prefix() -> None:
    """All discovered controls must have the Ctl prefix."""
    all_paths = _STEP_PATHS + _MESH_PATHS
    bad = [p for p in all_paths if not p.name.startswith("Ctl")]
    assert not bad, f"Non-Ctl files discovered in control directories: {bad}"


def test_at_least_ten_step_controls() -> None:
    """Sanity: we should have at least 10 STEP control fixtures."""
    assert len(_STEP_PATHS) >= 10, (
        f"Only {len(_STEP_PATHS)} STEP controls found under {_STEP_CONTROLS}; "
        "expected at least 10"
    )


def test_at_least_two_mesh_controls() -> None:
    """Sanity: we should have at least 2 mesh control fixtures."""
    assert len(_MESH_PATHS) >= 2, (
        f"Only {len(_MESH_PATHS)} mesh controls found under {_MESH_CONTROLS}; "
        "expected at least 2"
    )


# ── STEP controls: validate2 ───────────────────────────────────────────────────

_SHAPE_RE = re.compile(r"^shape\(\d+\)$")


@pytest.mark.parametrize("stp", _STEP_PATHS, ids=_STEP_IDS)
def test_step_control_occt_heal_on(stp: Path) -> None:
    """validate2 must return shape(N) (not empty/reject/signal) from occt_heal_on."""
    from step_corpus.validate2 import validate
    result = validate(stp)
    summary = result["summary"]
    status = summary.get("occt_heal_on", "")
    assert _SHAPE_RE.match(status), (
        f"{stp.name}: occt_heal_on={status!r} — expected shape(N). "
        f"Oracle pipeline over-rejects clean input."
    )


@pytest.mark.parametrize("stp", _STEP_PATHS, ids=_STEP_IDS)
def test_step_control_occt_heal_off(stp: Path) -> None:
    """validate2 must return shape(N) from occt_heal_off (no healing needed on clean input)."""
    from step_corpus.validate2 import validate
    result = validate(stp)
    summary = result["summary"]
    status = summary.get("occt_heal_off", "")
    assert _SHAPE_RE.match(status), (
        f"{stp.name}: occt_heal_off={status!r} — expected shape(N). "
        f"Oracle pipeline over-rejects clean input even without healing."
    )


@pytest.mark.parametrize("stp", _STEP_PATHS, ids=_STEP_IDS)
def test_step_control_structural(stp: Path) -> None:
    """The structural linter must return "ok" on every clean control — a
    linter that flags valid input is worse than useless (false-positive guard)."""
    from step_corpus._structural_oracle import lint_file
    code = lint_file(stp)
    assert code == "ok", (
        f"{stp.name}: structural linter returned {code!r} on a CLEAN control — "
        f"false positive. The structural oracle must not flag valid input."
    )


@pytest.mark.parametrize("stp", _STEP_PATHS, ids=_STEP_IDS)
def test_step_control_part21_strict(stp: Path) -> None:
    """part21_strict must accept all clean STEP controls."""
    from step_corpus.validate2 import validate
    result = validate(stp)
    summary = result["summary"]
    status = summary.get("part21_strict", "")
    assert status == "accept", (
        f"{stp.name}: part21_strict={status!r} — expected 'accept'. "
        f"Part-21 validator rejects clean input."
    )


# ── STEP controls: schema_oracle ───────────────────────────────────────────────

@pytest.mark.parametrize("stp", _STEP_PATHS, ids=_STEP_IDS)
def test_step_control_schema_oracle_no_violations(stp: Path) -> None:
    """schema_oracle must report zero violations for clean AP214 controls."""
    from step_corpus._schema_oracle import check_fixture
    result = check_fixture(stp)
    violations = result.get("violations", [])
    assert not violations, (
        f"{stp.name}: schema_oracle found violations: {violations}. "
        f"Schema oracle over-reports on clean AP214 input."
    )


# ── Lint APIs: documentation of non-applicability ─────────────────────────────

def test_fixture_lint_not_applicable_documented() -> None:
    """_fixture_lint and _category_lint operate on catalog entries, not control files.

    Controls are not catalog entries — they have no catalog ID, no
    STEP_PROBLEM_CATALOG.md section, and no Expected/Tier-3 fields.
    The lint APIs take a catalog entry dict as input; there is no entry dict
    to pass for controls.

    This test documents that exclusion explicitly: if a future refactor makes
    _fixture_lint callable on arbitrary paths, add a parametrized test here.
    """
    from step_corpus import catalog
    ctl_ids = set(_STEP_IDS) | set(_MESH_IDS)
    catalog_ids = {e["id"] for e in catalog.iter_canonical()}
    # No control may appear in the catalog → lint will never be called on them
    assert not (ctl_ids & catalog_ids), (
        "A control ID appeared in the catalog; lint exclusion logic must be revisited."
    )


# ── Mesh controls: _mesh_oracle ────────────────────────────────────────────────

@pytest.mark.parametrize("mesh", _MESH_PATHS, ids=_MESH_IDS)
def test_mesh_control_no_assertion_failures(mesh: Path) -> None:
    """_mesh_oracle must report no 'fail' status on any clean mesh control.

    Clean controls have zero assertions — the oracle returns an empty
    assertion_results list, so there is nothing to fail.  If a future control
    adds positive assertions (e.g. edge_shared_by_2) those must also pass.
    """
    from step_corpus._mesh_oracle import check_one
    report = check_one(mesh)
    failures = [
        (a, r)
        for a, r in report.get("assertion_results", [])
        if r["status"] == "fail"
    ]
    assert not failures, (
        f"{mesh.name}: mesh oracle found failures:\n"
        + "\n".join(f"  {a}: {r}" for a, r in failures)
    )


@pytest.mark.parametrize("mesh", _MESH_PATHS, ids=_MESH_IDS)
def test_mesh_control_has_geometry(mesh: Path) -> None:
    """Clean mesh controls must have at least 4 vertices and 4 triangles."""
    from step_corpus._mesh_oracle import check_one
    report = check_one(mesh)
    assert report["n_vertices"] >= 4, (
        f"{mesh.name}: only {report['n_vertices']} vertices — degenerate control"
    )
    assert report["n_triangles"] >= 4, (
        f"{mesh.name}: only {report['n_triangles']} triangles — degenerate control"
    )
