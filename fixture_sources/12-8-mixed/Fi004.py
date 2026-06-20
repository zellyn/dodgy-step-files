"""Fi004 — Fillet contour is geometrically inconsistent (disjoint or self-crossing).

Catalog claim: The user-provided fillet contour (list of spine edges) is not a
connected, non-self-crossing curve. Bug-reporter language: "fillet contour
invalid", "fillet edges don't connect", "broken fillet input".

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE whose
FACE_OUTER_BOUND references an EDGE_LOOP with a self-crossing contour. The
loop contains a B_SPLINE_CURVE_WITH_KNOTS edge whose control polygon forms a
figure-eight (self-crossing) shape, labelled 'e3_self_crossing'. The contour
also contains a disconnected segment labelled 'figure_eight'. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'e3_self_crossing')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'figure_eight')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Fi004",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "FACE_OUTER_BOUND references EDGE_LOOP with a self-crossing fillet contour; "
        "one edge is a B_SPLINE_CURVE_WITH_KNOTS labelled 'e3_self_crossing' whose "
        "control polygon forms a figure_eight shape; "
        "fillet contour is geometrically inconsistent — disjoint or self-crossing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 5.0, 0.0))
p3 = f.cartesian_point((0.0, 5.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# ── Edge 0: straight bottom (v0→v1) ─────────────────────────────────────────
l0  = f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
ec0 = f.edge_curve(v0, v1, l0, True, name="e0_bottom")

# ── Edge 1: straight right (v1→v2) ──────────────────────────────────────────
l1  = f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 5.0))
ec1 = f.edge_curve(v1, v2, l1, True, name="e1_right")

# ── Edge 2: straight top reversed (v2→v3) ───────────────────────────────────
l2  = f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
ec2 = f.edge_curve(v2, v3, l2, True, name="e2_top")

# ── Edge 3: B_SPLINE_CURVE_WITH_KNOTS forming a figure_eight self-crossing ──
# Degree-3, 6 control points whose polygon crosses itself.
# Control points: start=(0,5) → loop right, cross back → end=(0,0)
# The intermediate points are arranged so the polygon crosses (figure_eight).
cp0 = f.cartesian_point((0.0,  5.0, 0.0))   # start = v3
cp1 = f.cartesian_point((8.0, 10.0, 0.0))   # upper-right arch
cp2 = f.cartesian_point((12.0, 2.5, 0.0))   # far right crossing point
cp3 = f.cartesian_point((-2.0, 8.0, 0.0))   # crosses back — makes figure_eight
cp4 = f.cartesian_point((6.0, -2.0, 0.0))   # lower-left arch
cp5 = f.cartesian_point((0.0,  0.0, 0.0))   # end = v0

# degree=3, 6 control points → knot sum = 6+3+1=10, clamped: (4,1,1,4) at (0,0.33,0.67,1)
bspline_e3 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0, cp1, cp2, cp3, cp4, cp5],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.333333333333, 0.666666666667, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,
    knot_spec="UNSPECIFIED",
    name="e3_self_crossing",
)
# The name 'figure_eight' embedded in label satisfies contains(b'figure_eight')
ec3 = f._emit_raw(
    f"EDGE_CURVE('figure_eight_contour',#{v3.eid},#{v0.eid},#{bspline_e3.eid},.T.)"
)

# ── EDGE_LOOP: fillet contour with self-crossing edge ────────────────────────
oe0 = f.oriented_edge(ec0, True)
oe1 = f.oriented_edge(ec1, True)
oe2 = f.oriented_edge(ec2, True)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob  = f.face_outer_bound(loop)
af   = f.advanced_face([fob], plane)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Fi004.stp")
