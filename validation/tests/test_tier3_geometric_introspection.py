"""Smoke tests for the B2.5b tier-3 introspection extensions:
B-spline / Bezier surface and curve properties, per-edge curve_type +
orientation, and per-face edge-loop orientation counts.

These ensure the new ``face[i].bspline.*``, ``face[i].edge_orientations.*``,
``edge[i].curve_type``, ``edge[i].orientation``, ``edge[i].bspline.*``
paths are populated whenever the geometry warrants it, and that
_tier3_assertions._resolve_lhs walks them correctly.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from step_corpus._tier3_assertions import _resolve_lhs

ROOT = Path(__file__).resolve().parents[2]
# Tfa225 = degree-1×2 B-spline face with 2 edges (both lines, reversed
# orientation in the wire). Stable corpus reference for this test.
BSPLINE_FIXTURE = ROOT / "step-examples" / "12-3c-faces" / "Tfa225.stp"


def _run_tier3(fixture: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "step_corpus.tier3_geometric", str(fixture), "--json"],
        capture_output=True, text=True, timeout=60,
    )
    raw = re.sub(r"\x1b\[[0-9;]*m", "", proc.stdout)
    return json.loads(raw[raw.find("{"):])


@pytest.fixture(scope="module")
def tier3_bspline() -> dict:
    assert BSPLINE_FIXTURE.is_file()
    return _run_tier3(BSPLINE_FIXTURE)


def test_face_bspline_props_populated(tier3_bspline: dict) -> None:
    f = tier3_bspline["faces"][0]
    assert f["surface_type"] == "bspline"
    bs = f["bspline"]
    # u/v degrees from a degree-1×2 patch
    assert bs["u_degree"] == 1
    assert bs["v_degree"] == 2
    # Properties surface as booleans, not nulls
    assert bs["is_rational"] is False
    assert bs["is_u_periodic"] is False
    assert bs["is_v_periodic"] is False
    # Knot vector summary
    assert bs["n_u_knots"] >= 2
    assert bs["n_v_knots"] >= 2
    assert bs["u_knot_mult_max"] >= 1
    assert bs["v_knot_mult_max"] >= 1


def test_face_edge_orientations_present(tier3_bspline: dict) -> None:
    eo = tier3_bspline["faces"][0]["edge_orientations"]
    assert set(eo.keys()) == {"forward", "reversed", "internal", "external"}
    # Total should equal the face's edge_count
    assert sum(eo.values()) == tier3_bspline["faces"][0]["edge_count"]


def test_edge_curve_type_and_orientation(tier3_bspline: dict) -> None:
    e = tier3_bspline["edges"][0]
    assert e["curve_type"] in {"line", "circle", "ellipse", "bspline",
                                "bezier", "hyperbola", "parabola", "offset",
                                "other"}
    assert e["orientation"] in {"forward", "reversed", "internal", "external"}


def test_resolve_lhs_walks_new_paths(tier3_bspline: dict) -> None:
    """End-to-end: confirm the assertion runner can walk the new paths."""
    cases = [
        ("face[0].surface_type", "bspline"),
        ("face[0].bspline.u_degree", 1),
        ("face[0].bspline.is_rational", False),
        ("face[0].bspline.is_u_periodic", False),
        ("edge[0].curve_type", "line"),
    ]
    for path, expected in cases:
        actual = _resolve_lhs(tier3_bspline, path)
        assert actual == expected, f"{path}: got {actual!r}, want {expected!r}"

    # `edge_orientations.<name>` walks correctly
    forward = _resolve_lhs(tier3_bspline, "face[0].edge_orientations.forward")
    reversed_ = _resolve_lhs(tier3_bspline, "face[0].edge_orientations.reversed")
    assert isinstance(forward, int)
    assert isinstance(reversed_, int)


def test_quadric_props_torus_introspection() -> None:
    """Torus surface yields major_radius, minor_radius, and axis_z."""
    fixture = ROOT / "step-examples" / "12-3c-faces" / "Tfa216.stp"
    if not fixture.is_file():
        pytest.skip(f"missing fixture {fixture}")
    d = _run_tier3(fixture)
    torus_faces = [f for f in d.get("faces", []) if f.get("surface_type") == "torus"]
    if not torus_faces:
        pytest.skip("Tfa216 no longer has torus face — fixture mutated")
    q = torus_faces[0].get("quadric")
    assert q is not None, "torus face must carry quadric props"
    assert q["major_radius"] == 2.0
    assert q["minor_radius"] == 0.5
    assert q["axis_z"] == 1.0


def test_quadric_props_cone_introspection() -> None:
    """Cone surface yields semi_angle and axis."""
    fixture = ROOT / "step-examples" / "12-2c-surfaces" / "Gs185.stp"
    if not fixture.is_file():
        pytest.skip(f"missing fixture {fixture}")
    d = _run_tier3(fixture)
    cone_faces = [f for f in d.get("faces", []) if f.get("surface_type") == "cone"]
    if not cone_faces:
        pytest.skip("Gs185 no longer has cone face")
    q = cone_faces[0].get("quadric")
    assert q is not None, "cone face must carry quadric props"
    assert q["semi_angle"] == 0.165
    # Cone axis can point in either direction; just verify it's a unit
    # vector along Z
    assert abs(abs(q["axis_z"]) - 1.0) < 1e-9


def test_quadric_props_sphere_introspection() -> None:
    """Sphere surface yields radius."""
    fixture = ROOT / "step-examples" / "12-2c-surfaces" / "Gs186.stp"
    if not fixture.is_file():
        pytest.skip(f"missing fixture {fixture}")
    d = _run_tier3(fixture)
    sphere_faces = [f for f in d.get("faces", []) if f.get("surface_type") == "sphere"]
    if not sphere_faces:
        pytest.skip("Gs186 no longer has sphere face")
    q = sphere_faces[0].get("quadric")
    assert q is not None, "sphere face must carry quadric props"
    assert q["radius"] == 5.0


def test_quadric_key_absent_on_non_quadric_surfaces(tier3_bspline: dict) -> None:
    """A B-spline face must NOT carry a `quadric` sub-dict."""
    for f in tier3_bspline.get("faces", []):
        if f.get("surface_type") in ("plane", "bspline", "bezier"):
            assert "quadric" not in f, (
                f"face {f.get('i')} surface_type={f.get('surface_type')} "
                f"has unexpected quadric: {f.get('quadric')}"
            )


def test_bspline_key_absent_on_non_bspline_surfaces() -> None:
    """A planar / cylindrical face must NOT carry a `bspline` sub-dict —
    the introspection helper returns None and the entry omits the key."""
    # Find any cached non-bspline fixture under /tmp/cad-v2-out-tier3
    # (it's faster than re-running validate on a planar STEP file).
    cache = Path("/tmp/cad-v2-out-tier3")
    if not cache.is_dir():
        pytest.skip("no tier-3 cache; populate via _run_corpus")
    for js in cache.rglob("*.json"):
        try:
            raw = re.sub(r"\x1b\[[0-9;]*m", "", js.read_text())
            d = json.loads(raw[raw.find("{"):])
        except Exception:
            continue
        for f in d.get("faces", []):
            if f.get("surface_type") == "plane":
                assert "bspline" not in f, (
                    f"{js.name} face[{f.get('i')}] is plane but has bspline key"
                )
                return
    pytest.skip("no planar faces in tier-3 cache")
