"""Twi128 — ShapeAnalysis_Wire.CheckTail tail-edge orientation flip.

Catalog claim: Wire's last edge declared with .F. (reverse) orientation;
CheckTail assumes trailing edge is always .T. and reports false, missing the
tail even when it should be detected.

Fixture: Rectangle EDGE_LOOP (4 main edges) with a small 5th tail edge appended
with .F. orientation. The tail edge goes from v4→v5_tail_start, parametrized
backwards. CheckTail fails to handle the orientation flip and misses the tail.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges:
  - e1..e4: rectangle loop (1mm × 1mm square), all .T. oriented
  - e5: small tail edge 0.0001mm, declared REVERSED (.F.) in the loop
    The EDGE_CURVE is stored v5→v4; in the loop the ORIENTED_EDGE uses .F.
    so the effective direction is v4→v5 (entering the tail). CheckTail
    looks at last ORIENTED_EDGE orientation, sees .F., assumes .T. is required,
    and fails to detect the tail IS the defect.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi128",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges; "
        "e1..e4: rectangle 1mm×1mm — (0,0,0)→(1,0,0)→(1,1,0)→(0,1,0)→(0,0,0) all .T.; "
        "e5: tail edge stored as EDGE_CURVE v5(0.0001,0,0)→v4(0,0,0), used .F. in loop; "
        "effective direction in loop: (0,0,0)→(0.0001,0,0) — very short 0.0001mm tail; "
        "CheckTail sees .F. orientation on last edge, assumes .T. required IS defect; "
        "orientation polarity assumption causes tail miss; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Rectangle vertices ────────────────────────────────────────────────────────
PA = (0.0,    0.0, 0.0)   # corner A
PB = (1.0,    0.0, 0.0)   # corner B
PC = (1.0,    1.0, 0.0)   # corner C
PD = (0.0,    1.0, 0.0)   # corner D
# Tail vertex: slightly off corner A
PT = (0.0001, 0.0, 0.0)   # tail tip (0.0001mm from A)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))
vT = f.vertex_point(f.cartesian_point(PT))


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1..e4: rectangle loop, all FORWARD in loop
e1  = f.edge_curve(vA, vB, _line(PA, PB))
oe1 = f.oriented_edge(e1, True)

e2  = f.edge_curve(vB, vC, _line(PB, PC))
oe2 = f.oriented_edge(e2, True)

e3  = f.edge_curve(vC, vD, _line(PC, PD))
oe3 = f.oriented_edge(e3, True)

e4  = f.edge_curve(vD, vA, _line(PD, PA))
oe4 = f.oriented_edge(e4, True)

# e5: tail edge stored vT→vA, but used REVERSED (.F.) in loop
# Effective direction in loop: vA → vT (0,0,0) → (0.0001,0,0)
e5 = f.edge_curve(vT, vA, _line(PT, PA))
# Use .F. orientation — CheckTail assumes .T., misses this tail
oe5 = f.oriented_edge(e5, False)  # REVERSED — IS the defect trigger

# ── EDGE_LOOP: 4 rectangle edges + 1 reversed tail ───────────────────────────
loop = f.edge_loop([oe1, oe2, oe3, oe4, oe5])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi128.stp")
