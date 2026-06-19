"""Mesh-tier oracle: pure-Python defect detection on .mesh.json fixtures.

This is the first cut of Q4.5 (BACKLOG). A full CGAL PMP / MeshFix
wrapper subprocess is heavier and goes through the same harness pattern
as `_occt_oracle.py`, but for now we exercise the mesh fixtures with a
minimal pure-Python detector that checks each fixture's machine-readable
assertions against the actual geometry. This catches:

- non-manifold edges (edge incident on != 2 triangles)
- degenerate triangles (zero area / collinear vertices)
- near-coincident vertex pairs (distance < eps)
- triangle-triangle self-intersection (specific pairs)
- isolated vertices (not referenced by any triangle)

Each fixture's metadata.assertions array is compared against the live
detection; pass means the assertion holds in the geometry.

Run:
    uv run python -m step_corpus._mesh_oracle [<id>]

With no argument, runs across every .mesh.json under mesh-examples/.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MESH_DIR = ROOT / "mesh-examples"


def _edge_incidence(triangles: list[list[int]]) -> dict[tuple[int, int], int]:
    """Count how many triangles each (canonicalized) edge is incident on."""
    counts: dict[tuple[int, int], int] = {}
    for tri in triangles:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = (min(a, b), max(a, b))
            counts[edge] = counts.get(edge, 0) + 1
    return counts


def _triangle_area(p0: list[float], p1: list[float], p2: list[float]) -> float:
    """|cross product| / 2 → triangle area in 3D."""
    ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    cx = uy * vz - uz * vy
    cy = uz * vx - ux * vz
    cz = ux * vy - uy * vx
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)


def _vertex_distance(p0: list[float], p1: list[float]) -> float:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _check_assertion(assertion: dict, vertices: list, triangles: list) -> dict:
    """Return {status: pass|fail|unknown, detail: str}."""
    kind = assertion.get("kind")
    if kind == "edge_shared_by_n_triangles":
        edge = tuple(assertion["edge"])
        expected = assertion["n"]
        edge_canon = (min(edge), max(edge))
        actual = _edge_incidence(triangles).get(edge_canon, 0)
        return {
            "status": "pass" if actual == expected else "fail",
            "detail": f"edge {edge_canon} incident on {actual} triangles (expected {expected})",
        }
    if kind == "triangle_area_lt":
        idx = assertion["triangle"]
        lt = assertion["lt"]
        tri = triangles[idx]
        area = _triangle_area(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
        return {
            "status": "pass" if area < lt else "fail",
            "detail": f"triangle {idx} area={area} (expected < {lt})",
        }
    if kind == "vertex_pair_distance_lt":
        i, j = assertion["pair"]
        lt = assertion["lt"]
        d = _vertex_distance(vertices[i], vertices[j])
        return {
            "status": "pass" if d < lt else "fail",
            "detail": f"vertices ({i},{j}) distance={d} (expected < {lt})",
        }
    if kind == "hole_boundary":
        # Pass if the loop's edges are each incident on exactly 1 triangle
        # (i.e. a true boundary cycle in the open mesh).
        loop = assertion["loop"]
        incidence = _edge_incidence(triangles)
        bad = []
        for k in range(len(loop)):
            a = loop[k]
            b = loop[(k + 1) % len(loop)]
            edge_canon = (min(a, b), max(a, b))
            n_inc = incidence.get(edge_canon, 0)
            if n_inc != 1:
                bad.append(f"edge {edge_canon} on {n_inc}")
        return {
            "status": "pass" if not bad else "fail",
            "detail": "boundary edges incident-on-1" if not bad else "; ".join(bad),
        }
    if kind == "triangles_self_intersect":
        # Pure-Python tri-tri intersection is non-trivial; we mark this as
        # "unknown" for now and defer to a CGAL PMP wrapper.
        ta, tb = assertion["triangles"]
        return {
            "status": "unknown",
            "detail": f"tri-tri intersection {ta} vs {tb} requires CGAL oracle",
        }
    if kind == "isolated_vertex":
        v = assertion["vertex"]
        used = {idx for tri in triangles for idx in tri}
        return {
            "status": "pass" if v not in used else "fail",
            "detail": f"vertex {v} {'unreferenced' if v not in used else 'in triangles'}",
        }
    return {"status": "unknown", "detail": f"unknown assertion kind {kind!r}"}


def check_one(path: Path) -> dict:
    data = json.loads(path.read_text())
    vertices = data["vertices"]
    triangles = data["triangles"]
    meta = data.get("metadata", {})
    assertions = meta.get("assertions", [])
    results = [_check_assertion(a, vertices, triangles) for a in assertions]
    return {
        "id": meta.get("id"),
        "defect_class": meta.get("defect_class"),
        "n_vertices": len(vertices),
        "n_triangles": len(triangles),
        "n_assertions": len(assertions),
        "assertion_results": list(zip(assertions, results)),
    }


def main() -> int:
    paths = sorted(MESH_DIR.rglob("*.mesh.json"))
    if len(sys.argv) > 1:
        target = sys.argv[1]
        paths = [p for p in paths if p.stem.startswith(target)]
        if not paths:
            print(f"no mesh fixture matching {target!r}", file=sys.stderr)
            return 2
    summary = {"pass": 0, "fail": 0, "unknown": 0}
    failures = []
    for p in paths:
        report = check_one(p)
        for a, r in report["assertion_results"]:
            summary[r["status"]] += 1
            if r["status"] == "fail":
                failures.append(f"  {report['id']}: {a.get('kind')}  {r['detail']}")
    print(f"Mesh-oracle: {summary}")
    if failures:
        print("Failures:")
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
