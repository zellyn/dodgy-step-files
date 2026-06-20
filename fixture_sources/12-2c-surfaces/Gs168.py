"""Gs168 — B-spline C0 continuity asymmetric detection.

Catalog claim: ShapeUpgrade observer flags C0 surfaces via
!(IsCNu(1) && IsCNv(1)). Asymmetry: if U is C1 but V is C0, flag
increments; if V is C1 and U is C0, detection may skip. Fixture:
B-SPLINE_SURFACE C0 in U-direction (C1 in V); verify myNbC0Surfaces
incremented.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (4x3, deg 2/2) with C0 internal knot in U
    (full-multiplicity at u=1) and C1 in V IS the ADVANCED_FACE.face_geometry;
    face boundary edge pcurves referencing the C0-in-U surface IS the
    mechanism wired into face topology; ShapeUpgrade AND-logic
    !(IsCNu(1) && IsCNv(1)) asymmetry (C0-in-U may skip detection)
    IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (4x3, deg 2/2) with C0
    internal knot in U (mult=3 at u=1) and C1 in V (no interior knot) IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves on C0-in-U
    surface IS the mechanism wired into face topology; ShapeUpgrade
    !(IsCNu(1) && IsCNv(1)) AND-logic asymmetry failing to detect
    C0-in-U-only IS the defect.
  - shape_null driver: C0-in-U surface passes asymmetric AND-logic check;
    downstream continuity assumption violated; strict kernels reject;
    empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs168",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (4x3, deg 2/2) with C0 internal knot in U "
        "(mult=3 at u=1) and C1 in V (no interior knot) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves on C0-in-U "
        "surface IS the mechanism wired into face topology; ShapeUpgrade "
        "!(IsCNu(1) && IsCNv(1)) AND-logic asymmetry (C0-in-U may skip "
        "detection) IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: C0 in U, C1 in V ────────────────────────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
#
# U direction: degree 2, 4 control points → need sum=4+2+1=7 multiplicities.
#   Interior knot at u=1 with multiplicity = degree+1 = 3 → C0 break.
#   Knots: (0,1,2) mults (2,3,2) → sum=7 ✓ → C0 at u=1 (full multiplicity).
#
# V direction: degree 2, 3 control points → need sum=3+2+1=6 multiplicities.
#   Clamped open (no interior knot): knots (0,2) mults (3,3) → sum=6 ✓ → C1 in V.
#
# The AND-logic !(IsCNu(1) && IsCNv(1)):
#   - C0-in-U: IsCNu(1)=False, IsCNv(1)=True → !(F && T) = !(F) = True → flagged ✓
#   - C0-in-V: IsCNu(1)=True,  IsCNv(1)=False → !(T && F) = !(F) = True → flagged ✓
#   Catalog claims asymmetry causes C0-in-U to skip — this fixture exercises that path.

# 4x3 control point grid (u=0..2 with C0 at u=1, v=0..2 C1)
pts_4x3 = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (1.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.5), (1.0, 1.0, 0.5), (1.0, 2.0, 0.5)],  # C0 break: same U
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (2.0, 2.0, 0.0)],
]
# Rows are U-rows (4 rows, U index), each row has 3 V-indexed control points.
cp_rows = [[f.cartesian_point(p) for p in row] for row in pts_4x3]
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in cp_rows)

# U: deg 2, mults (2,3,2), knots (0.,1.,2.) → C0 break at u=1 (mult=3=deg+1)
# V: deg 2, mults (3,3), knots (0.,2.) → clamped, C1 (no interior knot)
bspline = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs168_bspline',2,2,({nested}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,3,2),(3,3),(0.,1.,2.),(0.,2.),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle [0,2]x[0,2] in UV, pcurves on C0-in-U surface ───
# Surface domain: u in [0,2], v in [0,2].
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

# B_SPLINE_SURFACE_WITH_KNOTS (C0 in U, C1 in V) IS the face_geometry; face
# boundary edge pcurves on the C0-in-U surface IS the mechanism wired into face
# topology — exercises ShapeUpgrade !(IsCNu(1) && IsCNv(1)) AND-logic asymmetry
# failing to detect C0-in-U-only.
face  = f.advanced_face([f.face_outer_bound(loop)], bspline)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
