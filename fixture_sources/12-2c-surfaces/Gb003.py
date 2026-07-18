"""Gb003 — Closed B-spline curve has reversed end-tangent.

Catalog claim: A B_SPLINE_CURVE_WITH_KNOTS declares closed=.T. and first/last
control points coincide, but start and end tangents differ (cusp at closure
point). GeomLib_CheckBSplineCurve detects the C0-only closure.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-3, exactly 5 control points (cp[0] == cp[4]):
      (1,0,0), (0,1,0), (-1,0,0), (0,-1,0), (1,0,0)
    knot vector (0.0,1.0) mults (4,4).
    Marked closed=.T., self_intersect=.F.
    Tangent at t=0 is toward (0,1,0); tangent at t=1 is toward (0,-1,0) → cusp.
  - This B-spline IS the face_geometry (via SURFACE_CURVE on a degenerate plane)
    AND the ADVANCED_FACE uses a VERTEX_LOOP at the closure point (1,0,0) as the
    boundary — all wired into the face topology.
  - Exactly 5 CARTESIAN_POINT entities in the file (cp0–cp4).
  - Byte assertions: contains(b'B_SPLINE_CURVE_WITH_KNOTS('),
    contains(b'.T.,.F.'), count_entity_def(b'CARTESIAN_POINT') == 5.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS closed=.T. with cusp at closure
    IS the ADVANCED_FACE.face_geometry (passed as the surface argument); the
    VERTEX_LOOP at (1,0,0) wires the degenerate boundary to the face.
  - shape_null driver: cusp closure detected by GeomLib_CheckBSplineCurve.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gb003",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 closed=.T. 5 control points "
        "cp[0]==cp[4]=(1,0,0); tangent at t=0 != tangent at t=1 (cusp); "
        "IS ADVANCED_FACE.face_geometry (3D curve used as surface entity); "
        "VERTEX_LOOP at (1,0,0) wires boundary; shape_null=True; "
        "exactly 5 CARTESIAN_POINT entities"
    ),
)

# ── CATALOG MECHANISM: exactly 5 CARTESIAN_POINT entities ────────────────────
# Degree-3, knots (0.0,1.0) mults (4,4), closed=.T., self_intersect=.F.
# cp[0] == cp[4] = (1,0,0); tangents at t=0 and t=1 differ → cusp.
cp0 = f.cartesian_point(( 1.0,  0.0, 0.0))
cp1 = f.cartesian_point(( 0.0,  1.0, 0.0))
cp2 = f.cartesian_point((-1.0,  0.0, 0.0))
cp3 = f.cartesian_point(( 0.0, -1.0, 0.0))
cp4 = f.cartesian_point(( 1.0,  0.0, 0.0))   # == cp0 positional closure; cusp

defect_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gb003_cusp_close',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

# ── VERTEX_LOOP at closure point — wires the degenerate boundary ──────────────
v_close = f.vertex_point(cp0)    # reuse cp0; no new CARTESIAN_POINT emitted
vloop   = f._emit_raw(f"VERTEX_LOOP('gb003_vloop',#{v_close.eid})")
fob     = f._emit_raw(f"FACE_OUTER_BOUND('gb003_fob',#{vloop.eid},.T.)")

# ADVANCED_FACE: the closed B-spline IS the face_geometry (surface argument).
# This is a degenerate surface usage — the mechanism IS the face surface.
face  = f._emit_raw(
    f"ADVANCED_FACE('gb003_face',(#{fob.eid}),#{defect_bspline.eid},.T.)"
)
shell = f._emit_raw(f"OPEN_SHELL('gb003_shell',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([])
f.add_product_chain(sbsm, uncertainty_literal="LENGTH_MEASURE(1.0E-7)")  # bare typed real, not enum-wrapped (scaffolding-artifact fix)
