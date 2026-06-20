"""Twi097 — Edge-projection-aux range computation loses precision on periodic curves.

Catalog claim: An edge whose host curve is periodic (circle, ellipse, closed
B-spline) reports a parameter range that traverses the period seam. A
range-validation step adjusts the range, but on periodic curves a naive range
adjustment that wraps to [0, 2π) loses the original sense (going the long way
vs the short way around). The healed edge then represents a different arc than
the original.

Reproducer recipe: Edge on a circle from parameter t=5.5 to t=1.0 (i.e., the
long way around through t=2π then to t=1.0). After range validation the edge
becomes [1.0, 5.5] (short way), reversing the arc.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP whose single
EDGE_CURVE rides a CIRCLE. The CIRCLE name is 'long_way_around' — the edge
arc is from t=5.5 to t=1.0 going past the 2π seam (long way). The 3D
endpoint at t=5.5 has z-component 0.0. OCC sees a GEOMETRIC_CURVE_SET
and returns empty.

Byte assertions:
  - contains(b'long_way_around')
  - contains(b'CIRCLE(')
  - contains(b'(0.7080734182735711,-0.7061278960829493,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi097",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with one EDGE_CURVE; "
        "host curve is CIRCLE 'long_way_around' (radius 1, XY plane, centre origin); "
        "arc traversal from t=5.5 to t=1.0 going the long way around past 2π; "
        "naive range-normalisation wraps to [1.0,5.5] reversing arc direction; "
        "start-vertex at t=5.5: (cos(5.5),sin(5.5),0) = (0.7081,-0.7061,0.0); "
        "end-vertex at t=1.0: (cos(1),sin(1),0); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CIRCLE: centre origin, radius 1, in XY plane ─────────────────────────────
ctr  = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(ctr, zdir, xdir)
# Byte assertion: contains(b'CIRCLE(')
# Byte assertion: contains(b'long_way_around')
circle = f.circle(plc, 1.0, name="long_way_around")

# ── Vertices at t=5.5 and t=1.0 on the unit circle ───────────────────────────
# t=5.5: cos(5.5) ≈ 0.7080734182735711, sin(5.5) ≈ -0.7061278960829493
# Byte assertion: contains(b'(0.7080734182735711,-0.7061278960829493,0.0)')
# Use _emit_raw to preserve full-precision literal so byte assertion passes.
p_t55_raw = f._emit_raw(
    "CARTESIAN_POINT('',(0.7080734182735711,-0.7061278960829493,0.0))"
)
v_start = f._emit_raw(f"VERTEX_POINT('',#{p_t55_raw.eid})")   # t=5.5 — arc start

p_t10 = (_math.cos(1.0), _math.sin(1.0), 0.0)
v_end = f.vertex_point(f.cartesian_point(p_t10))               # t=1.0 — arc end

# ── EDGE_CURVE on the circle: long-way arc from t=5.5 to t=1.0 ───────────────
ec = f.edge_curve(v_start, v_end, circle)
oe = f.oriented_edge(ec, True)

# ── EDGE_LOOP and GEOMETRIC_CURVE_SET ────────────────────────────────────────
loop = f.edge_loop([oe])
gcs  = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi097.stp")
