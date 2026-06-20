"""Gs082 — ShapeAnalysis_Surface.NextValueOfUV curvature step-size.

Catalog claim: B_SPLINE_SURFACE with sharp peak (Z=5.0 at center). Newton
iteration for surface point location exhibits curvature-driven step collapse
below epsilon tolerance before convergence.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS (biquadratic, center pole Z=5.0 sharp peak)
    IS the ADVANCED_FACE.face_geometry; sharp central peak (high curvature,
    Z=5.0) IS the mechanism wired into face topology; NextValueOfUV Newton
    step collapses below epsilon before convergence IS the defect.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS'),
                     contains(b'5.0').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS (3×3 biquadratic, center
    pole at Z=5.0 creating sharp peak) IS the ADVANCED_FACE.face_geometry;
    sharp curvature peak at center IS the mechanism wired into face topology;
    NextValueOfUV Newton step-size collapses below epsilon IS the defect.
  - shape_null driver: Newton iteration fails to converge; strict kernels
    reject non-convergent UV location; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs082",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (3×3 biquadratic, center pole Z=5.0 sharp peak) "
        "IS ADVANCED_FACE.face_geometry; sharp curvature peak at center (Z=5.0) IS "
        "the mechanism wired into face topology; NextValueOfUV Newton step-size "
        "collapses below epsilon before convergence IS the defect; shape_null"
    ),
)

# ── 3×3 biquadratic B-spline: sharp central peak at Z=5.0 ────────────────────
# Control grid: degree 2×2, 3×3 poles.
# Peripheral poles at Z=0; center pole (1,1) at Z=5.0 creates high curvature.
# Byte assertion: contains(b'5.0')
ctrl = [
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 0.5, 0.0), (0.5, 0.5, 5.0), (1.0, 0.5, 0.0)],   # Z=5.0 at center
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (1.0, 1.0, 0.0)],
]

ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]

cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(3)) + ")"
    for r in range(3)
) + ")"

# Byte assertion: contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs082_bss',2,2,"
    f"{cp_str},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square on the sharp-peak surface ──────────────────────
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

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry; sharp Z=5.0 peak IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
