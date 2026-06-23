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


def _triangle_normal(p0: list[float], p1: list[float], p2: list[float]) -> tuple[float, float, float]:
    """Return the (un-normalized) normal vector (cross product) of a triangle."""
    ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    return (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)


def _vertex_distance(p0: list[float], p1: list[float]) -> float:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _triangle_adjacency(triangles: list[list[int]]) -> dict[tuple[int, int], list[int]]:
    """Map each canonical edge to the list of triangle indices incident on it."""
    adj: dict[tuple[int, int], list[int]] = {}
    for ti, tri in enumerate(triangles):
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = (min(a, b), max(a, b))
            adj.setdefault(edge, []).append(ti)
    return adj


def _triangles_intersect(
    a0: list[float], a1: list[float], a2: list[float],
    b0: list[float], b1: list[float], b2: list[float],
    eps: float = 1e-12,
) -> bool:
    """Triangle-triangle intersection (Möller 1997).

    Returns True iff the two triangles share a 1D or 2D set of points other
    than purely a shared vertex or a fully-shared edge with no interior
    crossing. Designed for defect detection on .mesh.json fixtures, not
    for general computational-geometry use — coplanar pairs are flagged
    as intersecting when their 2D projections overlap with positive area.

    Algorithm sketch:
      * Compute plane equation of triangle B (normal Nb, offset db).
      * Signed distances d_A_i of triangle A's vertices to plane B.
      * If all d_A have the same sign (and none zero), A is on one side
        of plane B → no intersection.
      * Mirror check for triangle A's plane vs B.
      * Otherwise compute the line L = plane_A ∩ plane_B; project the
        portion of each triangle that crosses its other-plane onto L,
        yielding two parametric intervals [t1, t2]; intersection iff
        the intervals overlap with positive length.
      * Coplanar case (Nb·Na nearly parallel + distance ≈ 0): fall back
        to 2D containment test.
    """
    def _sub(p, q):
        return [p[0] - q[0], p[1] - q[1], p[2] - q[2]]

    def _cross(u, v):
        return [u[1] * v[2] - u[2] * v[1],
                u[2] * v[0] - u[0] * v[2],
                u[0] * v[1] - u[1] * v[0]]

    def _dot(u, v):
        return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]

    def _signed_dist(p, n, d):
        return n[0] * p[0] + n[1] * p[1] + n[2] * p[2] - d

    # Plane of triangle B
    nb = _cross(_sub(b1, b0), _sub(b2, b0))
    db = _dot(nb, b0)
    da0 = _signed_dist(a0, nb, db)
    da1 = _signed_dist(a1, nb, db)
    da2 = _signed_dist(a2, nb, db)
    # Snap tiny distances to zero
    if abs(da0) < eps: da0 = 0.0
    if abs(da1) < eps: da1 = 0.0
    if abs(da2) < eps: da2 = 0.0
    if da0 * da1 > 0 and da0 * da2 > 0:
        # All A vertices strictly on the same side of plane B → no cross.
        return False

    # Plane of triangle A
    na = _cross(_sub(a1, a0), _sub(a2, a0))
    da = _dot(na, a0)
    db0 = _signed_dist(b0, na, da)
    db1 = _signed_dist(b1, na, da)
    db2 = _signed_dist(b2, na, da)
    if abs(db0) < eps: db0 = 0.0
    if abs(db1) < eps: db1 = 0.0
    if abs(db2) < eps: db2 = 0.0
    if db0 * db1 > 0 and db0 * db2 > 0:
        return False

    # Coplanar fallback: planes are parallel and the offset ≈ 0.
    # Project to a 2D coordinate frame and test 2D triangle overlap.
    D = _cross(na, nb)
    if _dot(D, D) < eps:
        # Coplanar. Pick the axis-aligned plane with largest normal
        # component to drop one coordinate.
        ax = max(range(3), key=lambda i: abs(na[i]))
        i1, i2 = [j for j in range(3) if j != ax]

        def _proj(p):
            return (p[i1], p[i2])

        return _tri2d_overlap([_proj(a0), _proj(a1), _proj(a2)],
                              [_proj(b0), _proj(b1), _proj(b2)], eps)

    # Compute the parametric intervals along L = plane_A ∩ plane_B.
    # Choose the dominant axis of D for projection.
    ax = max(range(3), key=lambda i: abs(D[i]))
    p_a = (a0[ax], a1[ax], a2[ax])
    p_b = (b0[ax], b1[ax], b2[ax])
    t_a = _interval(p_a, (da0, da1, da2))
    t_b = _interval(p_b, (db0, db1, db2))
    if t_a is None or t_b is None:
        return False
    lo = max(t_a[0], t_b[0])
    hi = min(t_a[1], t_b[1])
    # Positive-length overlap → real intersection.
    return hi - lo > eps


def _interval(proj: tuple, dist: tuple) -> tuple[float, float] | None:
    """Compute scalar interval [tmin, tmax] where the triangle crosses the
    other plane, projected along the chosen axis.

    The two endpoints of the intersection line segment lie on the
    triangle edges whose endpoints have opposite signs of `dist` (or
    where one endpoint has dist == 0).
    """
    crossings: list[float] = []
    for i in range(3):
        j = (i + 1) % 3
        di, dj = dist[i], dist[j]
        pi, pj = proj[i], proj[j]
        if di == 0 and dj == 0:
            # Edge lies in the other plane — both endpoints are crossings.
            crossings.append(pi)
            crossings.append(pj)
        elif di == 0:
            crossings.append(pi)
        elif di * dj < 0:
            # Strict sign change → linear interp to find the zero crossing.
            t = di / (di - dj)
            crossings.append(pi + t * (pj - pi))
    if not crossings:
        return None
    return (min(crossings), max(crossings))


def _tri2d_overlap(a: list, b: list, eps: float) -> bool:
    """Coplanar fallback: 2D triangle-triangle overlap (SAT)."""
    def _edge_cross(p, q, r):
        # 2D z-component of (q-p) × (r-p)
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def _proj_extent(tri, axis):
        # Project triangle vertices onto axis (a 2D unit-ish vector); return [min, max].
        ps = [v[0] * axis[0] + v[1] * axis[1] for v in tri]
        return min(ps), max(ps)

    # Separating-Axis test: for each edge of each triangle, normal axis.
    for tri in (a, b):
        for i in range(3):
            p, q = tri[i], tri[(i + 1) % 3]
            edge = (q[0] - p[0], q[1] - p[1])
            axis = (-edge[1], edge[0])  # 2D normal
            a_lo, a_hi = _proj_extent(a, axis)
            b_lo, b_hi = _proj_extent(b, axis)
            # Strict-less-or-equal: a "just touching at a vertex" coplanar
            # pair has a_hi == b_lo on the separating axis; we want to
            # reject those as non-intersecting since the shared point
            # alone isn't a defect.
            if a_hi <= b_lo + eps or b_hi <= a_lo + eps:
                return False
    return True


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
        ta, tb = assertion["triangles"]
        a = triangles[ta]
        b = triangles[tb]
        intersects = _triangles_intersect(
            vertices[a[0]], vertices[a[1]], vertices[a[2]],
            vertices[b[0]], vertices[b[1]], vertices[b[2]],
        )
        return {
            "status": "pass" if intersects else "fail",
            "detail": f"tri-tri intersection {ta} vs {tb}: {'crosses' if intersects else 'no cross'}",
        }
    if kind == "isolated_vertex":
        v = assertion["vertex"]
        used = {idx for tri in triangles for idx in tri}
        return {
            "status": "pass" if v not in used else "fail",
            "detail": f"vertex {v} {'unreferenced' if v not in used else 'in triangles'}",
        }
    if kind == "duplicate_triangle_pair":
        ta, tb = assertion["triangles"]
        key_a = tuple(sorted(triangles[ta]))
        key_b = tuple(sorted(triangles[tb]))
        match = key_a == key_b
        return {
            "status": "pass" if match else "fail",
            "detail": f"triangle {ta} sorted={key_a}, triangle {tb} sorted={key_b}",
        }
    if kind == "triangle_normal_z_negative":
        idx = assertion["triangle"]
        tri = triangles[idx]
        nx, ny, nz = _triangle_normal(vertices[tri[0]], vertices[tri[1]], vertices[tri[2]])
        return {
            "status": "pass" if nz < 0.0 else "fail",
            "detail": f"triangle {idx} normal z={nz:.6g} (expected < 0)",
        }
    if kind == "vertex_on_edge":
        v = assertion["vertex"]
        a, b = assertion["edge"]
        pv, pa, pb = vertices[v], vertices[a], vertices[b]
        # (pv - pa) × (pb - pa) must be ~zero, and t ∈ [0,1].
        dx, dy, dz = pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]
        ex, ey, ez = pv[0] - pa[0], pv[1] - pa[1], pv[2] - pa[2]
        cx = ey * dz - ez * dy
        cy = ez * dx - ex * dz
        cz = ex * dy - ey * dx
        cross_len = math.sqrt(cx * cx + cy * cy + cz * cz)
        edge_len = math.sqrt(dx * dx + dy * dy + dz * dz)
        # t = (pv-pa)·(pb-pa) / |pb-pa|²
        dot = ex * dx + ey * dy + ez * dz
        t = dot / (dx * dx + dy * dy + dz * dz) if edge_len > 0 else -1.0
        on_line = cross_len < 1e-9 * max(edge_len, 1.0)
        in_range = 0.0 <= t <= 1.0
        return {
            "status": "pass" if (on_line and in_range) else "fail",
            "detail": (f"vertex {v} on edge ({a},{b}): cross_len={cross_len:.3g} t={t:.4g}"
                       f" on_line={on_line} in_range={in_range}"),
        }
    if kind == "triangle_aspect_ratio_gt":
        idx = assertion["triangle"]
        gt = assertion["gt"]
        tri = triangles[idx]
        p0, p1, p2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
        area = _triangle_area(p0, p1, p2)
        e0 = _vertex_distance(p0, p1)
        e1 = _vertex_distance(p1, p2)
        e2 = _vertex_distance(p2, p0)
        longest = max(e0, e1, e2)
        # Aspect ratio: longest_edge / (2 * inradius) where inradius = area / s,
        # s = semi-perimeter. Equivalently: longest * (e0+e1+e2) / (4 * area).
        s = (e0 + e1 + e2)
        if area < 1e-30:
            ratio = float("inf")
        else:
            ratio = longest * s / (4.0 * area)
        return {
            "status": "pass" if ratio > gt else "fail",
            "detail": f"triangle {idx} aspect_ratio={ratio:.4g} (expected > {gt})",
        }
    if kind == "vertex_fan_disconnected":
        v = assertion["vertex"]
        # Build list of triangles incident on v.
        incident = [ti for ti, tri in enumerate(triangles) if v in tri]
        if len(incident) < 2:
            return {
                "status": "fail",
                "detail": f"vertex {v} has only {len(incident)} incident triangle(s); bowtie needs ≥2",
            }
        # BFS over incident triangles connected by shared non-v edges.
        adj = _triangle_adjacency(triangles)
        visited = {incident[0]}
        queue = [incident[0]]
        while queue:
            ti = queue.pop()
            for a, b in ((triangles[ti][0], triangles[ti][1]),
                          (triangles[ti][1], triangles[ti][2]),
                          (triangles[ti][2], triangles[ti][0])):
                edge = (min(a, b), max(a, b))
                for nb in adj.get(edge, []):
                    if nb in incident and nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
        disconnected = len(visited) < len(incident)
        return {
            "status": "pass" if disconnected else "fail",
            "detail": (f"vertex {v}: {len(incident)} incident triangles, "
                       f"{len(visited)} reachable from first → "
                       f"{'disconnected fan' if disconnected else 'fully connected fan'}"),
        }
    if kind == "adjacent_triangles_inconsistent_winding":
        ta, tb = assertion["triangles"]
        tri_a, tri_b = triangles[ta], triangles[tb]
        na = _triangle_normal(vertices[tri_a[0]], vertices[tri_a[1]], vertices[tri_a[2]])
        nb = _triangle_normal(vertices[tri_b[0]], vertices[tri_b[1]], vertices[tri_b[2]])
        dot = na[0] * nb[0] + na[1] * nb[1] + na[2] * nb[2]
        return {
            "status": "pass" if dot < 0.0 else "fail",
            "detail": f"triangles {ta} and {tb} normal dot={dot:.6g} (expected < 0 for inconsistent winding)",
        }
    if kind == "triangle_not_reachable_from":
        source = assertion["source"]
        target = assertion["target"]
        adj = _triangle_adjacency(triangles)
        visited = {source}
        queue = [source]
        while queue:
            ti = queue.pop()
            for a, b in ((triangles[ti][0], triangles[ti][1]),
                          (triangles[ti][1], triangles[ti][2]),
                          (triangles[ti][2], triangles[ti][0])):
                edge = (min(a, b), max(a, b))
                for nb in adj.get(edge, []):
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
        reachable = target in visited
        return {
            "status": "pass" if not reachable else "fail",
            "detail": f"triangle {target} {'reachable' if reachable else 'not reachable'} from {source}",
        }
    if kind == "duplicate_polygon_group":
        group = assertion["triangles"]
        expected_n = assertion["n"]
        if len(group) != expected_n:
            return {
                "status": "fail",
                "detail": f"group lists {len(group)} triangles but n={expected_n}",
            }
        keys = [tuple(sorted(triangles[ti])) for ti in group]
        all_same = len(set(keys)) == 1
        return {
            "status": "pass" if all_same else "fail",
            "detail": (f"group {group}: all share key {keys[0]}" if all_same
                       else f"group {group}: distinct keys {keys}"),
        }
    if kind == "reversed_polygon_pair":
        ta, tb = assertion["triangles"]
        tri_a = triangles[ta]
        tri_b = triangles[tb]
        key_a = tuple(sorted(tri_a))
        key_b = tuple(sorted(tri_b))
        if key_a != key_b:
            return {
                "status": "fail",
                "detail": f"triangles {ta} and {tb} have different vertex sets: {key_a} vs {key_b}",
            }
        # Check opposite winding: if same winding, cyclic rotation of a matches b.
        def _canonical_cycle(t):
            # Smallest-first cyclic rotation.
            m = min(range(3), key=lambda i: t[i])
            return (t[m], t[(m+1) % 3], t[(m+2) % 3])
        ca = _canonical_cycle(tri_a)
        cb = _canonical_cycle(tri_b)
        same_winding = ca == cb
        # Opposite winding means cb is the reverse: ca == (ca[0], ca[2], ca[1]) cycle.
        rev_ca = (ca[0], ca[2], ca[1])
        opposite_winding = _canonical_cycle(list(rev_ca)) == cb or rev_ca == cb
        return {
            "status": "pass" if (key_a == key_b and not same_winding) else "fail",
            "detail": (f"triangles {ta} and {tb}: same_vertex_set=True, same_winding={same_winding}"
                       f" tri_a={tri_a} tri_b={tri_b}"),
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
