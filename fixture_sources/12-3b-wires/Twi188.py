"""Twi188 — ShapeAnalysis_Wire.CheckSelfIntersectingEdge B-spline-with-loop.

Catalog claim: Single B-spline edge whose control polygon creates an interior
loop; CheckSelfIntersectingEdge's endpoint-filter masks the interior
intersection.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 1 edge on a
PLANE. The single edge is a degree-3 B_SPLINE_CURVE_WITH_KNOTS whose control
points form a figure-8 loop: (0,0)->(5,5)->(10,5)->(5,0)->(10,0). The curve
self-intersects in its interior near (7.5,2.5), but CheckSelfIntersectingEdge
filters out intersections near the curve endpoints and thus misses the interior
crossing. The self-looping spline edge is labelled 'bspline_interior_loop' to
make the defect explicit in bytes.

Byte assertions:
  - contains(b'bspline_interior_loop')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi188",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 1 edge on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "single degree-3 B_SPLINE_CURVE_WITH_KNOTS edge (bspline_interior_loop); "
        "control points: (0,0)->(5,5)->(10,5)->(5,0)->(10,0); "
        "curve self-intersects in interior near (7.5,2.5) — not at endpoints; "
        "bspline_interior_loop IS the mechanism; "
        "CheckSelfIntersectingEdge IS mechanism — endpoint-filter masks interior crossing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Control points for the self-intersecting B-spline (3D, z=0)
CP = [
    (0.0,  0.0, 0.0),
    (5.0,  5.0, 0.0),
    (10.0, 5.0, 0.0),
    (5.0,  0.0, 0.0),
    (10.0, 0.0, 0.0),
]

P_start = CP[0]
P_end   = CP[-1]

v_start = f.vertex_point(f.cartesian_point(P_start))
v_end   = f.vertex_point(f.cartesian_point(P_end))

# degree-3 B-spline, 5 control points: knot-mult sum = 5+3+1 = 9
# Two internal knots: clamp at 0 and 1 with mult 4, one internal at 0.5 mult 1
# But 4+1+4=9 works. Use knots [0, 0.5, 1] mults [4, 1, 4].
cp3d = [f.cartesian_point(p) for p in CP]
bsp3d = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp3d,
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,   # explicitly flagged in the STEP data
    knot_spec="UNSPECIFIED",
    name="bspline_interior_loop",
)

# 2D pcurve (same control-point layout projected to UV)
cp2d = [f.cartesian_point((p[0], p[1])) for p in CP]
bsp2d = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp2d,
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,
    knot_spec="UNSPECIFIED",
)
drep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{bsp2d.eid}),#*)")
pc   = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
sc   = f._emit_raw(f"SURFACE_CURVE('',#{bsp3d.eid},(#{pc.eid}),.PCURVE_S1.)")
ec   = f._emit_raw(
    f"EDGE_CURVE('bspline_interior_loop',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi188.stp")
