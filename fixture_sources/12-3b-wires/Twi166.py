"""Twi166 — ShapeFix_Wire.FixSelfIntersectingEdge near-grazing.

Catalog claim: Single edge with two near-coincident points (self-intersection
within Confusion); FixSelfIntersectingEdge tries to split at near-degenerate
point.

Mechanism: A B-spline curve loops back on itself so that the "self-intersection"
point is only 0.0001 unit from the start, well above OCCT's Confusion (~1e-7)
but within the range that FixSelfIntersectingEdge tries to split. The split
creates topologically invalid sub-edges (near-zero length). The fixture encodes
this as a single-face planar shape so OCCT can load it as shape(1).

The wire contains:
  - E0: degree-3 B-spline that starts at P0=(0,0,0), swings out through the
        control-polygon hull, and returns to P_near=(0.0001,0,0) — endpoints
        are 0.0001 apart (greater than Confusion but tiny enough to trigger the
        degenerate-split path in FixSelfIntersectingEdge).
  - E1: short LINE from P_near=(0.0001,0,0) back to P0=(0,0,0) to close the
        wire.

The near-self-intersection IS the defect. FixSelfIntersectingEdge inspects the
B-spline for interior intersections and finds a "split" point very close to the
endpoint; without degenerate-split filtering it produces a sub-edge of length
~0.0001 that is topologically invalid.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi166",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 2 edges: "
        "E0 degree-3 B-spline from P0=(0,0,0) to P_near=(0.0001,0,0) looping "
        "out through (8,6,0) and back — endpoints separated by 0.0001, "
        "near-coincident but above Confusion; "
        "E1 LINE from P_near=(0.0001,0,0) back to P0=(0,0,0) closes the wire; "
        "B-spline near-grazing self-intersection IS the defect; "
        "FixSelfIntersectingEdge tries to split at near-degenerate point within "
        "Confusion creating topologically invalid sub-edges IS mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
# P0 is the main start/close vertex; P_near is 0.0001 away — above Confusion
# (~1e-7) but within the range that triggers FixSelfIntersectingEdge's
# degenerate-split path.
P0    = (0.0,    0.0, 0.0)
P_near = (0.0001, 0.0, 0.0)

v_P0    = f.vertex_point(f.cartesian_point(P0))
v_Pnear = f.vertex_point(f.cartesian_point(P_near))

# ── E0: degree-3 B-spline from P0 → P_near, looping out and back ─────────────
# 6 control points, degree 3 → knots sum = 6+3+1 = 10
# Control polygon: start at (0,0,0), swing out wide through (4,8,0) and (10,4,0),
# curve back through (6,-3,0) and (1,0.2,0), end at (0.0001,0,0).
# The curve comes back very close to its start — this IS the near-grazing defect.
cp0_e0 = f.cartesian_point((0.0,    0.0,  0.0))
cp1_e0 = f.cartesian_point((4.0,    8.0,  0.0))
cp2_e0 = f.cartesian_point((10.0,   4.0,  0.0))
cp3_e0 = f.cartesian_point((6.0,   -3.0,  0.0))
cp4_e0 = f.cartesian_point((1.0,    0.2,  0.0))
cp5_e0 = f.cartesian_point((0.0001, 0.0,  0.0))

bsp_e0 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_e0, cp1_e0, cp2_e0, cp3_e0, cp4_e0, cp5_e0],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.25, 0.75, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
e0  = f.edge_curve(v_P0, v_Pnear, bsp_e0, True)
oe0 = f.oriented_edge(e0, True)

# ── E1: short LINE from P_near → P0 (closes the wire) ────────────────────────
e1_line = f.line(
    f.cartesian_point(P_near),
    f.vector(f.direction((-1.0, 0.0, 0.0)), 0.0001),
)
e1  = f.edge_curve(v_Pnear, v_P0, e1_line, True)
oe1 = f.oriented_edge(e1, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe0, oe1])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi166.stp")
