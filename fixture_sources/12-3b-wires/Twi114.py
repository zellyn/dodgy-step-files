"""Twi114 — ShapeFix_Wire.FixTails tail-elimination.

Catalog claim: Wire ending in a small "tail" edge (length 0.05 units) much
shorter than its neighbors (length 10.0). Tail extends from (0,10) to (0,10.05).
FixTails should identify and remove this degenerate edge to restore wire closure.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with three edges:
  - e1: LINE from (0,0,0) to (10,0,0) — normal bottom edge, length 10
  - e2: LINE from (10,0,0) to (0,10,0) — normal diagonal, length ~14.14
  - e3: LINE from (0,10,0) to (0,10.05,0) — tail edge, length 0.05 (IS defect)
The tail e3 extends slightly past the natural closure point; FixTails should
detect that it is much shorter than its neighbours and remove it.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi114",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges; "
        "e1: LINE (0,0,0)→(10,0,0) length 10.0 (normal); "
        "e2: LINE (10,0,0)→(0,10,0) length ~14.14 (normal); "
        "e3: LINE (0,10,0)→(0,10.05,0) length 0.05 — tail edge IS defect; "
        "tail is 200x shorter than neighbours; "
        "FixTails should detect and remove degenerate tail edge; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ───────────────────────────────────────────────────────────────────
P0 = (0.0,   0.0,  0.0)
P1 = (10.0,  0.0,  0.0)
P2 = (0.0,  10.0,  0.0)
P3 = (0.0,  10.05, 0.0)   # tail end point (IS defect)

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


# e1: normal bottom edge, length 10
e1  = f.edge_curve(v0, v1, _line(P0, P1))
oe1 = f.oriented_edge(e1, True)

# e2: normal diagonal, length ~14.14
e2  = f.edge_curve(v1, v2, _line(P1, P2))
oe2 = f.oriented_edge(e2, True)

# e3: tail edge, length 0.05 — IS defect
e3  = f.edge_curve(v2, v3, _line(P2, P3))
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe1, oe2, oe3])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi114.stp")
