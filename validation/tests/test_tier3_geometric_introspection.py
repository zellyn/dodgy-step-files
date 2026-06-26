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
