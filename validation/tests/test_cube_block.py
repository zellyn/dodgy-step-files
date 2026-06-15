"""Self-tests for the canonical-cube fixture-generator module.

The cube generator emits a closed 6-face cube with the topology
invariant that every EDGE_CURVE is used exactly once with .T. and
once with .F. across its two incident faces. This test re-validates
that invariant from the module's actual output (so any future change
to the winding rules is caught immediately).
"""
from __future__ import annotations

import re

from step_corpus._cube_block import cube


ORIENTED_EDGE_RE = re.compile(
    r"=ORIENTED_EDGE\('[^']*'\s*,\s*\*\s*,\s*\*\s*,\s*#(\d+)\s*,\s*\.([TF])\.\s*\)"
)


def _edge_orientation_uses(body: str) -> dict[int, list[str]]:
    """Return {edge_curve_id: [sense, sense]} across all ORIENTED_EDGEs."""
    uses: dict[int, list[str]] = {}
    for m in ORIENTED_EDGE_RE.finditer(body):
        uses.setdefault(int(m.group(1)), []).append(m.group(2))
    return uses


def test_outward_cube_has_consistent_winding() -> None:
    """Every edge of an outward-normal cube is used once .T. and once .F."""
    body, _ = cube(base=100, origin=(0, 0, 0), size=10.0, outward=True)
    uses = _edge_orientation_uses(body)
    assert len(uses) == 12, f"expected 12 edges, got {len(uses)}"
    for edge_id, senses in uses.items():
        assert sorted(senses) == ["F", "T"], (
            f"edge #{edge_id} used {senses}; expected exactly one .T. and one .F."
        )


def test_inward_cube_also_has_consistent_winding() -> None:
    """outward=False (void-shell convention) must preserve the invariant
    — the loops are reversed, but each edge is still used once each way."""
    body, _ = cube(base=100, origin=(0, 0, 0), size=10.0, outward=False)
    uses = _edge_orientation_uses(body)
    assert len(uses) == 12
    for edge_id, senses in uses.items():
        assert sorted(senses) == ["F", "T"], (
            f"edge #{edge_id} used {senses}; expected one .T. and one .F."
        )


def test_cube_produces_expected_entity_counts() -> None:
    """A canonical cube has 8 vertices, 12 edges, 6 faces, 1 closed shell."""
    body, _ = cube(base=100, origin=(0, 0, 0), size=10.0)
    assert body.count("CARTESIAN_POINT") >= 8  # vertices + face centres
    assert body.count("VERTEX_POINT") == 8
    assert body.count("EDGE_CURVE") == 12
    assert body.count("EDGE_LOOP") == 6
    assert body.count("FACE_OUTER_BOUND") == 6
    assert body.count("ADVANCED_FACE") == 6
    assert body.count("CLOSED_SHELL") == 1


def test_id_ranges_dont_overlap_across_bases() -> None:
    """Two cubes with base=100 and base=400 must produce disjoint id ranges
    (so they can coexist in one fixture). The generator reserves ~260 ids
    per cube, so 100→359 and 400→659 should not collide."""
    body_a, shell_a = cube(base=100, origin=(0, 0, 0), size=10.0)
    body_b, shell_b = cube(base=400, origin=(0, 0, 0), size=10.0)
    ids_a = {int(m) for m in re.findall(r"^#(\d+)\s*=", body_a, re.MULTILINE)}
    ids_b = {int(m) for m in re.findall(r"^#(\d+)\s*=", body_b, re.MULTILINE)}
    assert ids_a.isdisjoint(ids_b), f"ids overlap: {ids_a & ids_b}"
    assert max(ids_a) < 400, f"base=100 cube reached id {max(ids_a)} (>=400)"
    assert min(ids_b) >= 400
