"""Twi232 — ShapeFix_Wire.FixSelfIntersection two-edges-two-intersections.

Catalog claim: Two edges that cross at TWO distinct points in 3D space.
FixSelfIntersection handles single intersection per edge pair only; with
multiple crossings, the second intersection remains undetected and unrepaired.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two B-spline
edges 'cross_e0' and 'cross_e1' that form an S-cross pattern, intersecting
at two distinct 3D points. FixSelfIntersection's single-intersection-per-pair
logic finds and handles the first crossing but ignores the second IS the defect.

Byte assertions:
  - contains(b'cross_e0')
  - contains(b'cross_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi232",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with two B-spline edges; "
        "cross_e0: degree-3 B-spline from (-6,0,0) to (6,0,0) arching upward IS first edge; "
        "cross_e1: degree-3 B-spline from (0,-6,0) to (0,6,0) arching rightward IS second edge; "
        "two edges cross at approximately (-2,2,0) AND (2,-2,0) IS two intersection points; "
        "FixSelfIntersection single-intersection-per-pair logic finds first crossing only; "
        "second intersection at (2,-2,0) remains undetected IS the defect mechanism; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z for pcurves
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# cross_e0: horizontal-ish B-spline arching up through middle
# Degree 3, 6 control points → knot sum = 10, multiplicities [4,1,1,4]
# Path: (-6,0,0) → left-high arch → (6,0,0), crossing the vertical edge twice
cp0_0 = f.cartesian_point((-6.0,  0.0, 0.0))
cp0_1 = f.cartesian_point((-3.0,  6.0, 0.0))
cp0_2 = f.cartesian_point((-1.0, -3.0, 0.0))
cp0_3 = f.cartesian_point(( 1.0,  3.0, 0.0))
cp0_4 = f.cartesian_point(( 3.0, -6.0, 0.0))
cp0_5 = f.cartesian_point(( 6.0,  0.0, 0.0))

bspl_e0 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_0, cp0_1, cp0_2, cp0_3, cp0_4, cp0_5],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.33, 0.67, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
    name="cross_e0_3d",
)

# cross_e1: vertical-ish B-spline arching right through middle
# Path: (0,-6,0) → right-side arch → (0,6,0), crossing the horizontal edge twice
cp1_0 = f.cartesian_point(( 0.0, -6.0, 0.0))
cp1_1 = f.cartesian_point(( 6.0, -3.0, 0.0))
cp1_2 = f.cartesian_point((-3.0, -1.0, 0.0))
cp1_3 = f.cartesian_point(( 3.0,  1.0, 0.0))
cp1_4 = f.cartesian_point((-6.0,  3.0, 0.0))
cp1_5 = f.cartesian_point(( 0.0,  6.0, 0.0))

bspl_e1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp1_0, cp1_1, cp1_2, cp1_3, cp1_4, cp1_5],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.33, 0.67, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
    name="cross_e1_3d",
)

# Pcurves: straight-line approximations in UV space
def _straight_pcurve(uv_s, uv_e):
    du = uv_e[0] - uv_s[0]; dv = uv_e[1] - uv_s[1]
    mag = _math.sqrt(du*du + dv*dv)
    pc_orig = f.cartesian_point(uv_s)
    pc_dir  = f.direction((du/mag, dv/mag))
    pc_vec  = f.vector(pc_dir, mag)
    pc_ln   = f.line(pc_orig, pc_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_ln.eid}),#*)")
    return f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")


pc0 = _straight_pcurve((-6.0, 0.0), (6.0, 0.0))
pc1 = _straight_pcurve((0.0, -6.0), (0.0, 6.0))

sc0 = f._emit_raw(f"SURFACE_CURVE('',#{bspl_e0.eid},(#{pc0.eid}),.PCURVE_S1.)")
sc1 = f._emit_raw(f"SURFACE_CURVE('',#{bspl_e1.eid},(#{pc1.eid}),.PCURVE_S1.)")

v_e0_start = f.vertex_point(f.cartesian_point((-6.0, 0.0, 0.0)))
v_e0_end   = f.vertex_point(f.cartesian_point(( 6.0, 0.0, 0.0)))
v_e1_start = f.vertex_point(f.cartesian_point(( 0.0, -6.0, 0.0)))
v_e1_end   = f.vertex_point(f.cartesian_point(( 0.0,  6.0, 0.0)))

ec0 = f._emit_raw(f"EDGE_CURVE('cross_e0',#{v_e0_start.eid},#{v_e0_end.eid},#{sc0.eid},.T.)")
ec1 = f._emit_raw(f"EDGE_CURVE('cross_e1',#{v_e1_start.eid},#{v_e1_end.eid},#{sc1.eid},.T.)")

oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi232.stp")
