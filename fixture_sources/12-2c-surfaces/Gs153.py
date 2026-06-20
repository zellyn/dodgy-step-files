"""Gs153 — CalcMaxDegree knot multiplicity mismatch.

Catalog claim: ShapeAnalysis_Surface::CalcMaxDegree() computes the effective
degree of a B-spline surface by inspecting knot multiplicities. When the sum
of multiplicities does not equal n+p+1 (where n = number of control points and
p = degree), the effective-degree calculation returns an incorrect value.
Downstream algorithms that rely on this degree (e.g., continuity checkers,
surface splitters) make wrong decisions about the surface.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (3x3, deg 2/2) with intentionally mismatched
    knot multiplicities (sum != n+p+1 in U direction) IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing the
    mismatched knot surface IS the mechanism wired into face topology;
    CalcMaxDegree incorrect effective-degree from multiplicity mismatch IS the
    defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (3x3, deg 2/2) with
    mismatched U knot multiplicities (declared sum=5, required=6 for n=3,p=2)
    IS ADVANCED_FACE.face_geometry; face boundary edge pcurves on the
    mismatched-knot surface IS the mechanism wired into face topology;
    CalcMaxDegree incorrect effective-degree return IS the defect.
  - shape_null driver: wrong effective degree; downstream continuity/split
    decisions wrong; strict kernels reject invalid knot vector; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs153",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (3x3, deg 2/2) with mismatched U knot "
        "multiplicities (declared sum=5, required 6 for n=3 p=2) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves on mismatched-"
        "knot surface IS the mechanism wired into face topology; CalcMaxDegree "
        "incorrect effective-degree from multiplicity mismatch IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: 3x3, deg 2/2, mismatched U multiplicities ───
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Degree 2 in U: n=3 control points → valid knot sum = n+p+1 = 3+2+1 = 6.
# Intentional mismatch: U multiplicities (1,1,1) → sum=3 (knots 0,1,2) but
# with only 3 distinct knots and mult [1,1,1] OCCT expects a clamped vector.
# We use (2,1,2) → sum=5 instead of required 6 — one knot short.
# V is valid: deg 2, n=3, knots (0,1,2) mult (1,1,1) ... also (2,1,2) to mirror.
# The mismatch causes CalcMaxDegree to compute wrong effective degree.
pts_3x3 = [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.5), (2.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.5), (1.0, 1.0, 1.0), (2.0, 1.0, 0.5)],
    [(0.0, 2.0, 0.0), (1.0, 2.0, 0.5), (2.0, 2.0, 0.0)],
]
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_3x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# Mismatched U multiplicities: (2,1,2) → sum=5, required 6 for n=3 p=2.
# V multiplicities: (2,1,2) → same mismatch in V for symmetry.
# This is the knot-count inconsistency that CalcMaxDegree must handle.
bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs153_bspline',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,1,2),(2,1,2),(0.,1.,2.),(0.,1.,2.),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary referencing the mismatched-knot surface ────────────────────
# 3D corners approximate the surface corners at domain [0,2]x[0,2].
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

# B_SPLINE_SURFACE_WITH_KNOTS with mismatched multiplicities IS the face_geometry;
# face boundary edge pcurves on the mismatched-knot surface IS the mechanism
# wired into face topology — exercises CalcMaxDegree incorrect-degree-from-
# multiplicity-mismatch bug.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
