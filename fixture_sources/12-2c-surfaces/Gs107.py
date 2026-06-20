"""Gs107 — Closed-surface preservation in Bezier conversion.

Catalog claim: ShapeUpgrade_ConvertSurfaceToBezierBasis fails to preserve closure
when converting closed cylindrical surfaces to Bezier basis. The resulting Bezier
patches don't maintain seam closure or periodic boundary conditions.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius 1.0, height 1.0, closed in u: [0,2π]) IS the
    ADVANCED_FACE.face_geometry; face boundary spans full u-period [0,2π]
    with seam edge at u=0/2π IS the mechanism wired into face topology;
    ConvertSurfaceToBezierBasis converts the cylinder to Bezier patches without
    maintaining seam closure — resulting patches have gap at the seam IS the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE (radius=1.0) IS the
    ADVANCED_FACE.face_geometry; seam-edge at u=0/2π spanning full period
    IS the mechanism wired into face topology; ConvertSurfaceToBezierBasis
    does not preserve seam closure producing Bezier patches with gap IS the defect.
  - shape_null driver: seam-closure loss in Bezier conversion; strict kernels
    reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 2.0 * math.pi  # 6.283185307179586

f = StepFile(
    catalog_id="Gs107",
    defect=(
        "CYLINDRICAL_SURFACE (radius=1.0) IS ADVANCED_FACE.face_geometry; "
        "seam edge at u=0/6.283185307179586 spanning full u-period IS "
        "the mechanism wired into face topology; "
        "ConvertSurfaceToBezierBasis does not preserve seam closure, "
        "producing Bezier patches with gap at seam IS the defect; shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE radius 1.0, Z-axis ────────────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs107_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs107_cyl',#{cyl_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: full-period cylinder strip u:[0,2π], v:[0,1] ───────────────
# Seam edge at u=0/2π — the mechanism triggering closure-loss in Bezier conversion.
# 3D corners on cylinder radius 1, z∈[0,1]:
#   A: (1,0,0) at (u=0,   v=0)
#   B: (1,0,0) at (u=2π,  v=0)  — same 3D point (seam)
#   C: (1,0,1) at (u=2π,  v=1)  — same 3D point as D (seam)
#   D: (1,0,1) at (u=0,   v=1)
p_A = f.cartesian_point((1.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))   # seam: same 3D as A
p_C = f.cartesian_point((1.0, 0.0, 1.0))   # seam: same 3D as D
p_D = f.cartesian_point((1.0, 0.0, 1.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom circle A→B (v=0, u: 0→2π) — circumference arc, degenerate (same 3D point)
# 3D: circumference of unit circle at z=0; approximate length = TWO_PI
e0 = mk_edge_line(v_A, v_B,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.001,
                  (0.0, 0.0), (1.0, 0.0), TWO_PI)
# e1: seam line B→C (u=2π, v: 0→1) — seam edge, closure-critical
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (TWO_PI, 0.0), (0.0, 1.0), 1.0)
# e2: top circle C→D (v=1, u: 2π→0) — same 3D point
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 0.0, 1.0), (1.0, 0.0, 0.0), 0.001,
                  (TWO_PI, 1.0), (-1.0, 0.0), TWO_PI)
# e3: seam line D→A (u=0, v: 1→0) — seam edge at u=0
e3 = mk_edge_line(v_D, v_A,
                  (1.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE IS the face_geometry;
# full-period seam edge at u=0/2π IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
