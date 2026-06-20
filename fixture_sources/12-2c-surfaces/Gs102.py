"""Gs102 — ConvertSurfaceToBezierBasis: Bezier passthrough produces re-extracted copy.

Catalog claim: ShapeUpgrade_ConvertSurfaceToBezierBasis detects input is already
BEZIER_SURFACE and should return unmodified. Instead, algorithm extracts and
reconstructs Bezier, producing numerically different (re-extracted) surface.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - BEZIER_SURFACE (degree 2×2, 3×3 poles on unit square) IS the
    ADVANCED_FACE.face_geometry; face boundary follows the [0,1]×[0,1]
    parameter domain IS the mechanism wired into face topology;
    ConvertSurfaceToBezierBasis re-extracts the already-Bezier surface,
    producing numerically different poles IS the defect.
  - Byte assertions: contains(b'BEZIER_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: BEZIER_SURFACE (degree 2×2) IS the
    ADVANCED_FACE.face_geometry; face boundary on [0,1]×[0,1] domain IS
    the mechanism wired into face topology; ConvertSurfaceToBezierBasis
    re-extracts already-Bezier surface, changing poles numerically IS the defect.
  - shape_null driver: numerically altered re-extracted surface; strict kernels
    reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs102",
    defect=(
        "BEZIER_SURFACE (degree 2x2, 3x3 poles on unit square) IS "
        "ADVANCED_FACE.face_geometry; face boundary on [0,1]x[0,1] domain IS "
        "the mechanism wired into face topology; "
        "ConvertSurfaceToBezierBasis re-extracts already-Bezier surface "
        "producing numerically different poles IS the defect; shape_null"
    ),
)

# ── BEZIER_SURFACE degree 2×2, 3×3 poles on unit square ──────────────────────
# Byte assertion: contains(b'BEZIER_SURFACE')
ctrl = [
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.2), (1.0, 0.0, 0.0)],
    [(0.0, 0.5, 0.2), (0.5, 0.5, 0.5), (1.0, 0.5, 0.2)],
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.2), (1.0, 1.0, 0.0)],
]
ctrl_pts = [[f.cartesian_point(p) for p in row] for row in ctrl]
cp_str = "(" + ",".join(
    "(" + ",".join(f"#{ctrl_pts[r][c].eid}" for c in range(3)) + ")"
    for r in range(3)
) + ")"

bez = f._emit_raw(
    f"BEZIER_SURFACE('gs102_bez',2,2,{cp_str},.UNSPECIFIED.,.F.,.F.,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square [0,1]×[0,1] parameter domain ──────────────────
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
    pc  = f._emit_raw(f"PCURVE('pc',#{bez.eid},#{pcd.eid})")
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

# BEZIER_SURFACE IS the face_geometry; [0,1]x[0,1] boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], bez)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
