"""Gs162 — Surface C0 in single direction undetected.

Catalog claim: ShapeUpgrade continuity check uses AND logic (C1 in both U and V
required) instead of OR. Surfaces discontinuous in only one direction are not
flagged as C0. Requires B-spline with C1-U, C0-V knot multiplicity.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (3x4, deg 2/2) with C1 knot multiplicities
    in U but C0 (full-multiplicity internal knot) in V IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing the
    C0-in-V surface IS the mechanism wired into face topology;
    ShapeUpgrade AND-logic continuity check failing to flag C0-in-one-direction
    IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with C0 internal knot in V
    (multiplicity = degree+1 = 3 at interior knot) and C1 in U IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves on C0-in-V surface
    IS the mechanism wired into face topology; ShapeUpgrade AND-logic continuity
    check omitting C0-single-direction IS the defect.
  - shape_null driver: C0-in-V surface passes AND-logic check undetected;
    downstream continuity assumption violated; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs162",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (3x4, deg 2/2) with C0 internal knot in V "
        "(mult=3 at v=1) and C1 in U IS ADVANCED_FACE.face_geometry; face "
        "boundary edge pcurves on C0-in-V surface IS the mechanism wired into "
        "face topology; ShapeUpgrade AND-logic continuity check missing "
        "C0-single-direction IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: C1 in U, C0 in V ────────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
#
# U direction: degree 2, 3 control points → need sum=3+2+1=6 multiplicities.
#   Clamped open: knots (0,1,2) with mults (3,0,3) → sum=6. C1: no interior knot.
#   We use (3,3) for only 2 knots at 0 and 2 → sum=6 ✓ → C1 in U (no interior).
#
# V direction: degree 2, 4 control points → need sum=4+2+1=7 multiplicities.
#   Interior knot at v=1 with multiplicity = degree+1 = 3 → C0 break.
#   Knots: (0,1,2) mults (2,3,2) → sum=7 ✓ → C0 at v=1 (full multiplicity).
#
# The AND-logic check requires C1 in BOTH U and V to flag; C1-U AND C0-V → not
# flagged as C0, which is the defect.

# 3x4 control point grid (u=0..2, v=0..2 with interior break at v=1)
pts_3x4 = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 0.5), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (1.0, 1.0, 0.5), (1.0, 2.0, 0.0)],
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (2.0, 1.0, 0.5), (2.0, 2.0, 0.0)],
]
# Rows are U-rows (3 rows, U index), each row has 4 V-indexed control points.
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x4]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# U: deg 2, mults (3,3), knots (0.,2.) → clamped, C1 (no interior knot)
# V: deg 2, mults (2,3,2), knots (0.,1.,2.) → C0 break at v=1 (mult=3=deg+1)
bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs162_bspline',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(2,3,2),(0.,2.),(0.,1.,2.),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle [0,2]x[0,2] in UV, pcurves on C0-in-V surface ───
# Surface corners at domain corners: u in [0,2], v in [0,2].
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

# B_SPLINE_SURFACE_WITH_KNOTS (C0 in V, C1 in U) IS the face_geometry; face
# boundary edge pcurves on the C0-in-V surface IS the mechanism wired into face
# topology — exercises ShapeUpgrade AND-logic continuity check omitting
# C0-in-single-direction.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
