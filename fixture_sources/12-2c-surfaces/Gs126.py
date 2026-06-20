"""Gs126 — B-SPLINE_SURFACE with high-curvature Newton singularity.

Catalog claim: ShapeAnalysis_Surface.NextValueOfUV produces inf intermediate
when Newton's method is applied near a high-curvature region. The
clamping to finite value picks an arbitrary direction, leading to
incorrect UV projections and surface reference failures.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS with extreme curvature (degree=3, control
    points tightly folded so local curvature radius < tolerance) IS the
    ADVANCED_FACE.face_geometry; high-curvature singularity causing Newton
    divergence IS the mechanism wired into face topology;
    NextValueOfUV missing inf-guard IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (degree=3, control points
    folded to sub-tolerance curvature radius) IS ADVANCED_FACE.face_geometry;
    Newton singularity from extreme curvature IS the mechanism wired into face
    topology; NextValueOfUV inf-intermediate guard absence IS the defect.
  - shape_null driver: inf intermediate → clamped arbitrary direction →
    incorrect UV projection; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs126",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree=3, control points folded to "
        "extreme curvature so Newton Jacobian → singular) "
        "IS ADVANCED_FACE.face_geometry; "
        "high-curvature Newton singularity producing inf intermediate "
        "IS the mechanism wired into face topology; "
        "NextValueOfUV inf-guard absence IS the defect; "
        "shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: degree=3, highly folded control net ──────────
# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
# 4x2 control net; u-knots=(0,1) mults=(4,4) → 4 poles in U ✓
# v-knots=(0,1) mults=(2,2) → 2 poles in V ✓
# The middle two rows in U fold back sharply (y=±10) creating sub-tolerance
# curvature radius — Newton Jacobian becomes singular near fold apex.
ctrl = [
    [(0.0, 0.0, 0.0), (0.0, 0.0, 1.0)],
    [(0.5, 10.0, 0.0), (0.5, 10.0, 1.0)],
    [(0.5, -10.0, 0.0), (0.5, -10.0, 1.0)],
    [(1.0, 0.0, 0.0), (1.0, 0.0, 1.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(2)) + ")"
    for r in range(4)
) + ")"

bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs126_bss',3,1,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(2,2),"
    f"(0.0,1.0),"
    f"(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in parameter space ─────────────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 0.0, 1.0))
p_D = f.cartesian_point((0.0, 0.0, 1.0))

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

# Bottom: u from 0 to 1, v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# Right: v from 0 to 1, u=1
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# Top: u from 1 to 0, v=1
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 0.0, 1.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# Left: v from 1 to 0, u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS (folded, high curvature) IS the face_geometry;
# Newton singularity IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
