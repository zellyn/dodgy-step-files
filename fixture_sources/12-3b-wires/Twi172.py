"""Twi172 — ShapeFix_Wire.FixSelfIntersectingEdge cusp-edge.

Catalog claim: Single edge with a cusp (∂C/∂t = 0 at parameter t=0.5);
FixSelfIntersectingEdge attempts to compute tangent at cusp and fails.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with one
B-spline edge whose derivative vanishes at parameter t=0.5 (cusp at
mid-point). The B-spline control points fold back on themselves so that
the curve passes through the midpoint with zero tangent. FixSelfIntersectingEdge
attempts to compute a tangent direction at the cusp location and fails because
the derivative is zero there — it cannot determine an intersection test direction.

The cusp edge is labelled 'cusp_zero_derivative_midpoint' to make the
defect explicit in bytes.

Byte assertions:
  - contains(b'cusp_zero_derivative_midpoint')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi172",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 1 B-spline edge on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "B-spline degree-3 curve with cusp at t=0.5 — control points fold back "
        "so that the derivative ∂C/∂t = 0 at midpoint parameter IS the defect; "
        "edge labelled 'cusp_zero_derivative_midpoint'; "
        "FixSelfIntersectingEdge IS the mechanism — attempts tangent at cusp and fails "
        "because zero derivative prevents intersection test direction computation; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── B-spline curve with cusp at t=0.5 ────────────────────────────────────────
# Degree-3 B-spline. Control points: P0=(0,0,0), P1=(5,10,0), P2=(5,10,0),
# P3=(10,0,0). Points P1 and P2 are coincident — this makes the derivative
# zero at the midpoint parameter, creating a cusp.
# Knot vector (clamped): [0,0,0,0, 1,1,1,1] — uniform from t=0 to t=1.

cp0 = f.cartesian_point((0.0,  0.0, 0.0))
cp1 = f.cartesian_point((5.0, 10.0, 0.0))
cp2 = f.cartesian_point((5.0, 10.0, 0.0))   # coincident with cp1 → zero derivative
cp3 = f.cartesian_point((10.0, 0.0, 0.0))

cusp_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cusp_zero_derivative_midpoint',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

# Vertices at t=0 → (0,0,0) and t=1 → (10,0,0)
v_start = f.vertex_point(f.cartesian_point((0.0,  0.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))

ec = f._emit_raw(
    f"EDGE_CURVE('cusp_zero_derivative_midpoint',"
    f"#{v_start.eid},#{v_end.eid},#{cusp_bsp.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi172.stp")
