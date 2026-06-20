"""Os007 — Offset edge-extension step fails: clamped B_SPLINE_CURVE_WITH_KNOTS
has no analytic extension past its trim domain.

Catalog claim: An offset edge needs to be extended past its source endpoints to
meet a neighbouring offset edge, but the underlying curve cannot be evaluated
outside its domain (e.g., a B_SPLINE_CURVE_WITH_KNOTS with clamped boundary
knots has no analytic extrapolation).

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE whose
FACE_OUTER_BOUND references an EDGE_LOOP with a clamped B_SPLINE_CURVE_WITH_KNOTS
edge (degree 2, 3 control points, knot multiplicities (3,3) at (0,1)) which
cannot be analytically extended past its trim domain. The offset operation that
would need to extend this edge fails. OCC sees a GEOMETRIC_CURVE_SET and returns
empty.

Byte assertions:
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os007",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "FACE_OUTER_BOUND references EDGE_LOOP; "
        "one edge uses a clamped B_SPLINE_CURVE_WITH_KNOTS (degree 2, 3 ctrl pts, "
        "knot mults (3,3) at (0.0,1.0)) — cannot be evaluated outside its domain; "
        "offset edge-extension step fails: BRepOffset_MakeOffset CannotExtentEdge; "
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
p2 = f.cartesian_point((10.0, 8.0, 0.0))
p3 = f.cartesian_point((0.0, 8.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# ── Edge 0: straight bottom line v0→v1 ──────────────────────────────────────
l0  = f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
ec0 = f.edge_curve(v0, v1, l0, True, name="e0_bottom")

# ── Edge 1: straight right line v1→v2 ────────────────────────────────────────
l1  = f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 8.0))
ec1 = f.edge_curve(v1, v2, l1, True, name="e1_right")

# ── Edge 2: clamped B_SPLINE_CURVE_WITH_KNOTS v2→v3 ─────────────────────────
# Degree 2, 3 control points, clamped knots (3,3) at (0.0, 1.0).
# Cannot be evaluated outside [0,1] — the offset algorithm's CannotExtentEdge.
cp_a = f.cartesian_point((10.0, 8.0, 0.0))   # = v2
cp_b = f.cartesian_point(( 5.0, 9.0, 0.0))   # mid control point (arched top)
cp_c = f.cartesian_point(( 0.0, 8.0, 0.0))   # = v3

bspline_top = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp_a, cp_b, cp_c],
    knot_multiplicities=[3, 3],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
    name="clamped_top_edge",
)
ec2 = f.edge_curve(v2, v3, bspline_top, True, name="e2_clamped_bspline")

# ── Edge 3: straight left line v3→v0 ─────────────────────────────────────────
l3  = f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 8.0))
ec3 = f.edge_curve(v3, v0, l3, True, name="e3_left")

# ── EDGE_LOOP ────────────────────────────────────────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True),
    f.oriented_edge(ec3, True),
])
fob = f.face_outer_bound(loop)
af  = f.advanced_face([fob], plane)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os007.stp")
