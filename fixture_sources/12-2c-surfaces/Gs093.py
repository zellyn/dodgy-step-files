"""Gs093 — ShapeUpgrade_SplitSurface BSpline irregular knots.

Catalog claim: B-spline surface with irregular V knot multiplicities (3,1,3) on
4 control points. SplitSurface assumes uniform multiplicities, causing
over-subdivision and invalid knot structure.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (degree-2 in V, 4 V-poles, V knot mults (3,1,3)
    — irregular: interior multiplicity 1 instead of ≤degree=2) IS the
    ADVANCED_FACE.face_geometry; irregular interior knot multiplicity in V IS
    the mechanism wired into face topology; SplitSurface assumes uniform
    multiplicities, over-subdivides, produces invalid knot structure IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'3,1,3').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (degree 1×2, V knots
    mults=(3,1,3), 4 V control points — interior mult 1 is irregular for degree 2)
    IS the ADVANCED_FACE.face_geometry; irregular V knot multiplicities (3,1,3)
    IS the mechanism wired into face topology; SplitSurface over-subdivides on
    irregular mults, knot structure becomes invalid IS the defect.
  - shape_null driver: invalid knot structure after over-subdivision; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs093",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree 1 in U, degree 2 in V; V knot "
        "mults (3,1,3) — irregular interior mult=1 for degree-2) IS "
        "ADVANCED_FACE.face_geometry; irregular V knot multiplicities (3,1,3) "
        "IS the mechanism wired into face topology; SplitSurface over-subdivides "
        "on irregular mults, produces invalid knot structure IS the defect; shape_null"
    ),
)

# ── B-spline surface: degree 1 in U, degree 2 in V ───────────────────────────
# U: 2 poles, degree 1, knots (0,1) mults (2,2) — simple
# V: 4 poles, degree 2, knots (0,0.5,1) mults (3,1,3) — irregular interior mult
# For degree-2, interior mult should be ≤ 2; mult=1 is technically valid STEP
# but triggers the irregular-knot path in SplitSurface.
# Byte assertion: contains(b'3,1,3')
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 0.33, 0.0), (0.0, 0.67, 0.5), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 0.33, 0.0), (1.0, 0.67, 0.5), (1.0, 1.0, 0.0)],
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(4)) + ")"
    for r in range(2)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'), contains(b'3,1,3')
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs093_bss',1,2,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(3,1,3),"
    f"(0.0,1.0),"
    f"(0.0,0.5,1.0),.UNSPECIFIED.)"
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

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; irregular V mults (3,1,3) IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
