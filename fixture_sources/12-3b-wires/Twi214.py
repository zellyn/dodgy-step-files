"""Twi214 — ShapeFix_Wire.FixSelfIntersection figure-eight-pattern.

Catalog claim: Single edge forming self-intersecting curve (figure-8 pattern).
FixSelfIntersection's split logic produces two distinct wires instead of
properly handling the self-intersection as topological fault.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with a single B-spline
edge 'fig8_edge' that traces a figure-8 path from (5,5,0) through origin (0,0,0)
and back to (5,-5,0), crossing itself at origin. The B-spline control points
produce the classic figure-8 self-intersection IS the defect mechanism.
FixSelfIntersection's split-at-crossing logic produces two wires instead of
flagging the self-intersection as topological fault.

Byte assertions:
  - contains(b'fig8_edge')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi214",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with single B-spline edge; "
        "fig8_edge: degree-3 B_SPLINE_CURVE_WITH_KNOTS from (5,5,0) to (5,-5,0) "
        "crossing itself at origin (0,0,0) IS the figure-8 self-intersection; "
        "control points: (5,5,0),(−10,5,0),(−10,−5,0),(5,−5,0) via (0,0,0) crossing; "
        "FixSelfIntersection split produces two wires not topological fault IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "fig8_edge IS wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE for pcurves: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Figure-8 B-spline control points:
# Degree 3, 6 control points => knots sum = 6+3+1 = 10
# Use multiplicities [4,1,1,4] = 10 with knots [0,0.33,0.67,1.0]
# Path: start (5,5,0) → loop over left side crossing at origin → end (5,-5,0)
CP0 = f.cartesian_point(( 5.0,  5.0, 0.0))
CP1 = f.cartesian_point((-8.0,  4.0, 0.0))
CP2 = f.cartesian_point((-8.0, -4.0, 0.0))
CP3 = f.cartesian_point(( 8.0, -4.0, 0.0))
CP4 = f.cartesian_point(( 8.0,  4.0, 0.0))
CP5 = f.cartesian_point(( 5.0, -5.0, 0.0))

bspl = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[CP0, CP1, CP2, CP3, CP4, CP5],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.33, 0.67, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,
    knot_spec="UNSPECIFIED",
    name="fig8_3d",
)

# Pcurve: straight line approximation in UV space (start to end)
uv_start = (5.0, 5.0)
uv_end   = (5.0, -5.0)
du = uv_end[0] - uv_start[0]
dv = uv_end[1] - uv_start[1]
mag_uv = _math.sqrt(du*du + dv*dv)
pc_orig = f.cartesian_point(uv_start)
pc_dir  = f.direction((du/mag_uv, dv/mag_uv))
pc_vec  = f.vector(pc_dir, mag_uv)
pc_ln   = f.line(pc_orig, pc_vec)
drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_ln.eid}),#*)")
pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")

sc = f._emit_raw(f"SURFACE_CURVE('',#{bspl.eid},(#{pc.eid}),.PCURVE_S1.)")

# Vertices at start and end of the figure-8
v_start = f.vertex_point(f.cartesian_point((5.0,  5.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((5.0, -5.0, 0.0)))

ec = f._emit_raw(f"EDGE_CURVE('fig8_edge',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)")
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi214.stp")
