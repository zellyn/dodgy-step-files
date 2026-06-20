"""Twi131 — ShapeFix_Wire.FixLacking degenerate-edge insertion.

Catalog claim: Wire missing edge between two near-coincident vertices
(v4_degenerate→v4_degenerate); FixLacking must insert a degenerate edge but
cannot determine edge direction because start==end.

Fixture: 5-edge wire where edge4 jumps from v4(0,10,0) backwards to
v4_degenerate(5,5,0) (non-standard), and edge5 is a degenerate EDGE_CURVE
from v4_degenerate→v4_degenerate with parameter range 0.0 to 0.0 and undefined
direction. FixLacking must reconstruct this closure but has no geometric cue
for edge orientation.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi131",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges; "
        "e1: (0,0,0)→(10,0,0) bottom; e2: (10,0,0)→(10,10,0) right; "
        "e3: (10,10,0)→(0,10,0) top; e4: (0,10,0)→(5,5,0) backward jump (non-standard); "
        "e5: degenerate EDGE_CURVE (5,5,0)→(5,5,0) param range [0,0] undefined direction IS defect; "
        "FixLacking must insert degenerate edge but start==end gives no orientation cue; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ──────────────────────────────────────────────────────────────────
PA = (0.0,   0.0, 0.0)
PB = (10.0,  0.0, 0.0)
PC = (10.0, 10.0, 0.0)
PD = (0.0,  10.0, 0.0)
PG = (5.0,   5.0, 0.0)   # v4_degenerate (cone-apex / sphere-pole analogue)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))
vG = f.vertex_point(f.cartesian_point(PG))


def _line_edge(v_s, p_s, v_e, p_e):
    """Build an EDGE_CURVE with a straight LINE between two vertices."""
    dx, dy, dz = p_e[0]-p_s[0], p_e[1]-p_s[1], p_e[2]-p_s[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    crv = f.line(
        f.cartesian_point(p_s),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )
    return f.edge_curve(v_s, v_e, crv)


# e1..e3: valid rectangle edges
e1  = _line_edge(vA, PA, vB, PB)
oe1 = f.oriented_edge(e1, True)

e2  = _line_edge(vB, PB, vC, PC)
oe2 = f.oriented_edge(e2, True)

e3  = _line_edge(vC, PC, vD, PD)
oe3 = f.oriented_edge(e3, True)

# e4: backwards jump from vD→vG (non-standard gap edge)
e4  = _line_edge(vD, PD, vG, PG)
oe4 = f.oriented_edge(e4, True)

# e5: degenerate EDGE_CURVE vG→vG, zero-range parameter [0.0, 0.0]
# The curve is a zero-length B-spline (degree 1, two coincident control points)
# knot_multiplicities [2,2] => sum=4 = 2+1+1 ✓
degen_bsp = f.b_spline_curve_with_knots(
    degree=1,
    control_points=[
        f.cartesian_point(PG),
        f.cartesian_point(PG),   # coincident => zero-length IS defect
    ],
    knot_multiplicities=[2, 2],
    knots=[0.0, 0.0],            # zero-width knot span IS defect
)
e5  = f.edge_curve(vG, vG, degen_bsp)
oe5 = f.oriented_edge(e5, True)

# ── EDGE_LOOP: 5 edges ────────────────────────────────────────────────────────
loop = f.edge_loop([oe1, oe2, oe3, oe4, oe5])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi131.stp")
