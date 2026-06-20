"""Twi070 — Curve gap within a single edge: 3D curve and pcurve drift mid-edge.

Catalog claim: Along the interior of one edge, the 3D curve and the lifted
pcurve diverge by more than tolerance even though the endpoints agree. The
defect is invisible at endpoints; only mid-curve sampling reveals it.

Reproducer recipe: Edge whose 3D LINE goes from (0,0,0)→(10,0,0) straight,
but whose pcurve traces a slight arc through (5, 0.01) in UV — endpoints match,
mid-edge does not.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with one
SURFACE_CURVE edge on a CYLINDRICAL_SURFACE:
- 3D curve: straight LINE from (0,0,0) to (10,0,0)
- pcurve: B_SPLINE_CURVE_WITH_KNOTS of degree 2 whose control points trace
  a slight arc through UV (5.0, 0.01) — endpoints at (0,0) and (10,0) match
  the 3D line in UV mapping, but the interior bulges to (5.0, 0.01).
The mid-edge mismatch between the lifted pcurve and the 3D LINE is the defect.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'(5.0,0.01)')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS(')
  - contains(b'PCURVE(')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi070",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 1 SURFACE_CURVE edge; "
        "3D curve: straight LINE from (0,0,0) to (10,0,0); "
        "pcurve: B_SPLINE_CURVE_WITH_KNOTS degree 2 with endpoints (0,0) and (10,0) "
        "matching 3D endpoints in UV, but control point at (5.0,0.01) causes mid-edge "
        "pcurve arc to diverge from the 3D straight line; "
        "CheckCurveGaps detects mid-edge divergence only by sampling; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1 ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── 3D vertices: straight line endpoints ─────────────────────────────────────
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))

# ── 3D curve: straight LINE (0,0,0)→(10,0,0) ─────────────────────────────────
line_3d = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)
)

# ── pcurve: B_SPLINE_CURVE_WITH_KNOTS in UV — degree 2, 3 control points ─────
# Control points in UV space:
#   p0 = (0, 0)   — matches 3D start
#   p1 = (5.0, 0.01)   — mid-point bulge IS the byte assertion
#   p2 = (10, 0)  — matches 3D end
# Degree 2 (quadratic), knot vector [0,0,0,1,1,1].
# The lifted pcurve traces a parabolic arc through (5.0, 0.01), causing mid-edge
# divergence from the 3D straight LINE.
uv_p0 = f.cartesian_point((0.0,   0.0))
uv_p1 = f.cartesian_point((5.0,   0.01))   # byte assertion: (5.0,0.01)
uv_p2 = f.cartesian_point((10.0,  0.0))

bspline_uv = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[uv_p0, uv_p1, uv_p2],
    knot_multiplicities=[3, 3],
    knots=[0.0, 1.0],
)

drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{bspline_uv.eid}),#?)")
pcurve  = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

# ── SURFACE_CURVE: 3D LINE + drifting pcurve ─────────────────────────────────
sc = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP: single edge with mid-edge curve/pcurve divergence ─────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi070.stp")
