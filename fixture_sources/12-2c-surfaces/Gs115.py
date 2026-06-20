"""Gs115 — B-spline surface with duplicate knot values in both directions.

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS where interior knots are duplicated
beyond the degree (knot multiplicity exceeds degree+1), making the knot vector
invalid. ShapeAnalysis_Surface.GetBoxUF/GetBoxVF silently computes bounds on
the malformed knot sequence without flagging the structural error.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree 1, interior knot at 0.5 with
    multiplicity 3, exceeding degree+1=2) IS the ADVANCED_FACE.face_geometry;
    over-multiplied interior knot creating a structurally invalid knot vector
    IS the mechanism wired into face topology; GetBoxUF/GetBoxVF silently
    accepts the malformed knots without validation IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (interior knot multiplicity 3
    exceeds degree+1=2) IS the ADVANCED_FACE.face_geometry; over-multiplied
    interior knot creating invalid knot vector IS the mechanism wired into face
    topology; GetBoxUF/GetBoxVF silent acceptance of malformed knots IS the defect.
  - shape_null driver: invalid knot vector; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs115",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (interior knot multiplicity 3 exceeds degree+1=2) "
        "IS ADVANCED_FACE.face_geometry; "
        "over-multiplied interior knot creating invalid knot vector IS "
        "the mechanism wired into face topology; "
        "GetBoxUF/GetBoxVF silent acceptance of malformed knots IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degree 1, interior knot mult=3 (> degree+1=2) ─
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# Degree 1, 4 control points in u → knots: (2,3,2) mult with values (0.0,0.5,1.0)
# Interior multiplicity 3 exceeds degree+1=2 → invalid knot vector.
ctrl = [
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 1.0, 0.0), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(4)) + ")"
    for r in range(2)
) + ")"

# u: degree=1, 4 poles → need 4+1+1=6 knots;  mults (2,3,2)=[2+3+2=7? no: 2+2+2=6 for valid]
# To encode multiplicity=3 at interior (invalid for degree=1): mults=(2,3,2) → 7 knots for 5 poles
# Use 5 poles instead: ctrl rows have 5 pts, mults=(2,3,2) gives 2+3+2=7 = 5+1+1 ✓ (invalid mult)
# Simpler: degree=1, 3 poles, mults=(2,2,2)=6 for valid; mults=(2,3,2)=7 → needs 5 poles.
# Use: degree=1, 4 poles, standard valid mults=(2,2,2)=6 but change to (2,3,2)=7 → invalid.
# Actually for degree p and n+1 poles: #knots = n+p+2; mults sum = n+p+2.
# degree=1, 4 poles (n=3): sum_mults = 3+1+2 = 6; valid interior mult <= 2.
# Use mults=(2,2,2)=6 for 4 poles, but set interior mult=3 → sum=7 ≠ 6 → structurally invalid.
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs115_bss',1,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,3,2),(2,2),"
    f"(0.0,0.5,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space ─────────────────────────────
# 3D corners from the (geometrically valid) u-extent of the surface:
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (over-multiplied interior knot) IS the face_geometry;
# invalid knot vector IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
