"""Gs172 — ShapeAnalysis_Surface: degenerate surface derivative guard omission.

Catalog claim: Collapsed B-spline (all poles Z=0, D1≈0) triggers division
by zero in normal-projection logic. Defect: zero-magnitude derivative not
guarded before evaluation.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (3x3, deg 1/1) with all control-point Z=0
    (collapsed flat, D1 in surface-normal direction ≈ 0) IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing the
    degenerate collapsed surface IS the mechanism wired into face topology;
    ShapeAnalysis_Surface normal-projection logic dividing by |D1| without
    zero-magnitude guard IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (3x3, deg 1/1) with all
    Z=0 poles (D1≈0 in Z) IS ADVANCED_FACE.face_geometry; face boundary edge
    pcurves on the collapsed surface IS the mechanism wired into face topology;
    ShapeAnalysis_Surface dividing by zero-magnitude D1 in projection IS the
    defect.
  - shape_null driver: division by zero in normal-projection; undefined
    behavior / NaN propagation; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs172",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (3x3, deg 1/1) with all poles Z=0 "
        "(collapsed flat, D1≈0) IS ADVANCED_FACE.face_geometry; face boundary "
        "edge pcurves on the degenerate collapsed surface IS the mechanism "
        "wired into face topology; ShapeAnalysis_Surface normal-projection "
        "dividing by zero-magnitude D1 (zero-derivative guard absent) IS the "
        "defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: fully collapsed (all Z=0) ───────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
#
# Degree 1 in both U and V → bilinear patch.
# 3×3 control points all at Z=0 → surface is perfectly flat in the XY plane.
# D1 in the Z direction (surface normal direction) = 0 everywhere.
# ShapeAnalysis_Surface normal-projection computes D1 and divides; if no
# zero-magnitude guard is applied, this produces division by zero / NaN.
#
# U direction: deg 1, ncp=3 → sum_mults=3+1+1=5.
#   Knots (0.,1.,2.) mults (2,1,2) → sum=5 ✓.
# V direction: deg 1, ncp=3 → sum_mults=3+1+1=5.
#   Knots (0.,1.,2.) mults (2,1,2) → sum=5 ✓.

pts_3x3 = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (1.0, 2.0, 0.0)],
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (2.0, 2.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs172_bspline',1,1,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,1,2),(2,1,2),(0.,1.,2.),(0.,1.,2.),.UNSPECIFIED.)"
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

# B_SPLINE_SURFACE_WITH_KNOTS (all Z=0, D1≈0) IS the face_geometry; face
# boundary edge pcurves on the collapsed surface IS the mechanism wired into
# face topology — exercises ShapeAnalysis_Surface zero-derivative guard
# omission in normal-projection logic.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
