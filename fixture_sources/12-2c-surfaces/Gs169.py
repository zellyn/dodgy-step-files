"""Gs169 — ShapeAnalysis_Surface: rational surface knot-unaware sampling gap.

Catalog claim: Grid sampling in ShapeAnalysis_Surface omits knot-position
guards for rational B-spline surfaces; a triple knot at u=1.0 produces a
curvature discontinuity that the evaluation grid misses entirely.
Defect: knot multiplicity not honored in evaluation grid.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (rational, 4x3, deg 2/2) with triple knot
    at u=1.0 (mult=3=deg+1) IS the ADVANCED_FACE.face_geometry; face
    boundary edge pcurves referencing the rational B-spline surface IS the
    mechanism wired into face topology; ShapeAnalysis_Surface grid sampling
    skipping the knot position u=1.0 (knot-position guard absent) IS the defect.
  - Byte assertions: contains(b'RATIONAL_B_SPLINE_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: rational B_SPLINE_SURFACE_WITH_KNOTS (4x3, deg 2/2)
    with triple knot at u=1.0 IS ADVANCED_FACE.face_geometry; face boundary
    edge pcurves on the rational surface IS the mechanism wired into face
    topology; ShapeAnalysis_Surface grid sampling omitting knot-position
    guard at u=1.0 (curvature discontinuity missed) IS the defect.
  - shape_null driver: missed curvature discontinuity propagates into
    UV-projection logic; strict kernels reject on bad surface evaluation;
    empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs169",
    defect=(
        "rational B_SPLINE_SURFACE_WITH_KNOTS (4x3, deg 2/2) with triple knot "
        "at u=1.0 (mult=3=deg+1) IS ADVANCED_FACE.face_geometry; face boundary "
        "edge pcurves on the rational B-spline surface IS the mechanism wired "
        "into face topology; ShapeAnalysis_Surface grid sampling omitting "
        "knot-position guard at u=1.0 (curvature discontinuity missed) IS the "
        "defect; shape_null"
    ),
)

# ── RATIONAL_B_SPLINE_SURFACE (complex entity: B_SPLINE_SURFACE_WITH_KNOTS +
#    RATIONAL_B_SPLINE_SURFACE) ─────────────────────────────────────────────
# Byte assertion: contains(b'RATIONAL_B_SPLINE_SURFACE')
#
# U direction: degree 2, 4 control points.
#   sum of mults = ncp+deg+1 = 4+2+1 = 7.
#   Triple interior knot at u=1.0: mults (2,3,2) knots (0.,1.,2.) → C0 break.
#
# V direction: degree 2, 3 control points.
#   sum of mults = 3+2+1 = 6.
#   Clamped: mults (3,3) knots (0.,2.) → C1 (no interior knot).
#
# Weights: uniform 1.0 for all 12 poles (4x3 grid).
# The RATIONAL_B_SPLINE_SURFACE complex entity is used so the surface
# is classified as "rational"; ShapeAnalysis_Surface's grid sampler
# must insert a sample at each interior knot (u=1.0) for rational
# surfaces but the guard is absent, causing the C0 discontinuity to
# be skipped.

pts_4x3 = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.1), (1.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.4), (1.0, 1.0, 0.5), (1.0, 2.0, 0.4)],  # C0 break: same U
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (2.0, 2.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_4x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# Weights: all 1.0 (12 values in 4 rows of 3)
weights = "((1.,1.,1.),(1.,1.,1.),(1.,1.,1.),(1.,1.,1.))"

# Complex entity: B_SPLINE_SURFACE_WITH_KNOTS + RATIONAL_B_SPLINE_SURFACE
bspline = f._emit_raw(
    f"(B_SPLINE_SURFACE(2,2,({nested}),.UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((2,3,2),(3,3),(0.,1.,2.),(0.,2.),.UNSPECIFIED.)"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"RATIONAL_B_SPLINE_SURFACE({weights})"
    f"REPRESENTATION_ITEM('gs169_rbspline')"
    f"SURFACE())"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle [0,2]x[0,2] in UV ───────────────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((2.0, 0.0, 0.0))
p_C = f.cartesian_point((2.0, 2.0, 0.0))
p_D = f.cartesian_point((0.0, 2.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)


def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{bspline.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom: A→B, u=0→2 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (0.0, 0.0), (1.0, 0.0), 2.0)
# Right: B→C, v=0→2 at u=2
e1 = mk_edge_line(v_B, v_C,
                  (2.0, 0.0, 0.0), (0.0, 1.0, 0.0), 2.0,
                  (2.0, 0.0), (0.0, 1.0), 2.0)
# Top: C→D, u=2→0 at v=2
e2 = mk_edge_line(v_C, v_D,
                  (2.0, 2.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (2.0, 2.0), (-1.0, 0.0), 2.0)
# Left: D→A, v=2→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 2.0, 0.0), (0.0, -1.0, 0.0), 2.0,
                  (0.0, 2.0), (0.0, -1.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RATIONAL_B_SPLINE_SURFACE (triple knot at u=1.0) IS the face_geometry; face
# boundary edge pcurves on the rational surface IS the mechanism wired into face
# topology — exercises ShapeAnalysis_Surface grid sampling missing the knot-
# position guard.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
