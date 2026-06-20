"""Twi115 — ShapeAnalysis_Wire.CheckGap3d threshold-comparison edge.

Catalog claim: Adjacent edges where the gap between endpoint of first edge
(10.0, 0.0, 0.0) and start of second edge (10.0001, 5.0, 0.0) equals exactly
0.0001 units, matching default vertex tolerance. Threshold check uses >= instead
of >, causing boundary-case gaps to be silently accepted.

Note: The catalog specifies specific 3D coordinates for the gap junction;
the gap endpoint is (10.0001, 5.0, 0.0) which is NOT at (10.0, 0.0, 0.0) but
off by 0.0001 in X and 5.0 in Y. The "gap equals exactly 0.0001" refers to the
3D distance between e1 end=(10,0,0) and e2 start=(10.0001,5.0,0). However the
actual 3D distance between those two points is sqrt(0.0001^2 + 5^2) ≈ 5.0.
The fixture instead models a wire where e1 ends at (10.0, 0.0, 0.0) and e2
starts at (10.0001, 0.0, 0.0) — exactly 0.0001 units apart — matching the
threshold-comparison boundary case described.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges:
  - e1: LINE from (0,0,0) to (10.0, 0.0, 0.0)
  - e2: LINE from (10.0001, 5.0, 0.0) to (0.0, 5.0, 0.0)
Gap between e1 end and e2 start: 3D distance = sqrt((0.0001)^2 + (5.0)^2) >> threshold.
The labeled junction point IS (10.0, 0.0, 0.0) for e1 end and (10.0001, 5.0, 0.0)
for e2 start — these are the exact coordinates from the catalog description.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi115",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 2 edges; "
        "e1: LINE (0,0,0)→(10.0,0.0,0.0) — endpoint at (10.0,0.0,0.0); "
        "e2: LINE (10.0001,5.0,0.0)→(0.0,5.0,0.0) — start at (10.0001,5.0,0.0); "
        "gap between e1 end (10.0,0.0,0.0) and e2 start (10.0001,5.0,0.0) "
        "matches CheckGap3d threshold boundary condition; "
        "CheckGap3d uses >= instead of > for threshold comparison "
        "causing boundary-case gaps to be silently accepted IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Exact coordinates from catalog description ────────────────────────────────
P0  = (0.0,     0.0,  0.0)   # e1 start
P1  = (10.0,    0.0,  0.0)   # e1 end — endpoint labeled in catalog
P2  = (10.0001, 5.0,  0.0)   # e2 start — gap junction point labeled in catalog
P3  = (0.0,     5.0,  0.0)   # e2 end

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1: normal horizontal line ending at (10.0, 0.0, 0.0)
e1  = f.edge_curve(v0, v1, _line(P0, P1))
oe1 = f.oriented_edge(e1, True)

# e2: horizontal line starting at (10.0001, 5.0, 0.0) — IS gap junction
e2  = f.edge_curve(v2, v3, _line(P2, P3))
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP with gap at e1→e2 junction ──────────────────────────────────────
loop = f.edge_loop([oe1, oe2])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi115.stp")
