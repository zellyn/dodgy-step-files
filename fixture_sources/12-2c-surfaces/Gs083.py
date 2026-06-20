"""Gs083 — ShapeUpgrade_ConvertSurfaceToBezierBasis quasi-uniform vs non-uniform mismatch.

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS declared form='.QUASI_UNIFORM_KNOTS.'
but actual knots are non-uniform. Bezier converter follows form tag and produces
incorrect patch geometry.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (form=.QUASI_UNIFORM_KNOTS., actual knots non-uniform:
    (0.0, 0.3, 1.0)) IS the ADVANCED_FACE.face_geometry; form-tag vs actual-knot
    mismatch IS the mechanism wired into face topology; Bezier converter trusts
    form tag, produces incorrect patch geometry IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'QUASI_UNIFORM_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (form=.QUASI_UNIFORM_KNOTS.
    but knots 0.0,0.3,1.0 are non-uniform — uniform would be 0.0,0.5,1.0) IS
    the ADVANCED_FACE.face_geometry; quasi-uniform form tag with non-uniform actual
    knots IS the mechanism wired into face topology; Bezier converter uses form
    tag and produces wrong geometry IS the defect.
  - shape_null driver: incorrect Bezier patch from form-tag mismatch; strict
    kernels reject geometric inconsistency; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs083",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (form=.QUASI_UNIFORM_KNOTS. but actual knots "
        "non-uniform: 0.0,0.3,1.0 instead of 0.0,0.5,1.0) IS "
        "ADVANCED_FACE.face_geometry; quasi-uniform form tag vs non-uniform actual "
        "knots IS the mechanism wired into face topology; Bezier converter trusts "
        "form tag and produces incorrect patch geometry IS the defect; shape_null"
    ),
)

# ── B-spline surface: degree-2 in U, degree-1 in V ───────────────────────────
# U knots declared .QUASI_UNIFORM_KNOTS. but actual interior knot at 0.3 (not 0.5).
# Quasi-uniform for degree-2, 4 poles would require interior knot at 0.5.
# Using 0.3 makes the knot sequence genuinely non-uniform.
# U: 4 control points, degree 2, knots (0,0,0,0.3,1,1,1) mults (3,1,3)
# V: 2 control points, degree 1, knots (0,0,1,1) mults (2,2)
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(0.3, 0.0, 0.5), (0.3, 1.0, 0.5)],   # pole at u-knot 0.3 (non-uniform)
    [(0.7, 0.0, 0.5), (0.7, 1.0, 0.5)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(4)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
#                 contains(b'QUASI_UNIFORM_KNOTS')
# form=.QUASI_UNIFORM_KNOTS. but actual interior knot at 0.3 (non-uniform)
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs083_bss',2,1,"
    f"{cp_str},"
    f".QUASI_UNIFORM_KNOTS.,.F.,.F.,.F.,"
    f"(3,1,3),(2,2),"
    f"(0.0,0.3,1.0),"
    f"(0.0,1.0),.QUASI_UNIFORM_KNOTS.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square ────────────────────────────────────────────────
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

# e0: bottom A→B (v=0, u: 0→1)
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# e1: right B→C (u=1, v: 0→1)
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# e2: top C→D (v=1, u: 1→0)
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# e3: left D→A (u=0, v: 1→0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; quasi-uniform/non-uniform mismatch IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
