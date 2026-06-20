"""Sw008 — Fast-sewing cannot match candidate EDGE_CURVE to global edge table:
same endpoints but different underlying curves (LINE vs degree-1
B_SPLINE_CURVE_WITH_KNOTS).

Catalog claim: Two faces meet on what should be a shared edge, but each face's
boundary carries a different curve type for the same geometric locus (one LINE,
one degree-1 B_SPLINE_CURVE_WITH_KNOTS between the same endpoints).  The
fast-sewing lookup key does not match; hash mismatches.

Mechanism IS the shell / face topology: the file contains exactly 2 EDGE_CURVEs
— one referencing a LINE and one referencing a B_SPLINE_CURVE_WITH_KNOTS —
both on the same endpoint pair (0,0,0)→(1,0,0).  Both ARE wired into a single
EDGE_LOOP of the ADVANCED_FACE of the OPEN_SHELL (forward then reversed, as a
degenerate back-and-forth loop that presents the endpoint mismatch to the
fast-sewer).  The defect IS embedded in the face boundary topology.

Byte assertions:
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'LINE')
  - count_entity_def(b'EDGE_CURVE') == 2
Tier-3 assertions:
  - shape_null == True
OCC behavior: silently accepts (empty result).
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Sw008",
    defect=(
        "Exactly 2 EDGE_CURVEs between same endpoints (0,0,0)→(1,0,0): "
        "one using LINE and one using degree-1 B_SPLINE_CURVE_WITH_KNOTS; "
        "both ARE wired into EDGE_LOOP of ADVANCED_FACE of OPEN_SHELL; "
        "fast-sewing edge-table lookup key mismatch (curve-type differs) prevents stitching"
    ),
)

# ── Exactly 2 EDGE_CURVEs between the same endpoints ─────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)

# EDGE_CURVE 1: uses a LINE
d_x   = f.direction((1.0, 0.0, 0.0))
vec1  = f.vector(d_x, 1.0)
line  = f.line(p0, vec1)
ec_line = f.edge_curve(v0, v1, line)  # LINE-based, v0→v1

# EDGE_CURVE 2: uses a degree-1 B_SPLINE_CURVE_WITH_KNOTS on the same endpoints
# degree=1, 2 control points, knot mult [2,2], knots [0,1] → sum=4 = 2+1+1 ✓
bspl = f.b_spline_curve_with_knots(
    degree=1,
    control_points=[p0, p1],
    knot_multiplicities=[2, 2],
    knots=[0.0, 1.0],
)
ec_bspline = f.edge_curve(v0, v1, bspl)  # B_SPLINE-based, same v0→v1

# EDGE_LOOP: LINE edge forward, B_SPLINE edge reversed — same endpoints,
# different curve type; this is the input the fast-sewer fails to match
oe_fwd = f.oriented_edge(ec_line,   True)   # LINE v0→v1
oe_rev = f.oriented_edge(ec_bspline, False) # B_SPLINE v1→v0 (reversed)
loop   = f.edge_loop([oe_fwd, oe_rev])

# Plane for the face (required surface reference)
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# OPEN_SHELL IS the topology carrier — both EDGE_CURVEs ARE wired in via
# the EDGE_LOOP of the face's FACE_OUTER_BOUND
shell = f.open_shell([face], name="sw008_line_vs_bspline_edge")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
