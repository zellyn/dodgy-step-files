"""Gs104 — SURFACE_OF_REVOLUTION with profile-on-axis.

Catalog claim: ShapeAnalysis_Surface.IsDegenerated fails to detect degenerate
SURFACE_OF_REVOLUTION where the profile curve coincides with the axis of
revolution. The cross-product test produces near-zero result but is not
properly classified as singular.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION whose profile LINE lies exactly on the Z-axis
    (direction (0,0,1), passing through origin) IS the ADVANCED_FACE.face_geometry;
    face boundary spans u: [0, 2π], v: [0, 1] on the degenerate swept surface
    IS the mechanism wired into face topology; IsDegenerated() cross-product
    test produces near-zero result but is not classified as singular IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION (profile LINE on Z-axis) IS the
    ADVANCED_FACE.face_geometry; face boundary on degenerate swept surface IS
    the mechanism wired into face topology; IsDegenerated() cross-product
    underflow not classified singular IS the defect.
  - shape_null driver: profile coincides with revolution axis, zero-radius
    sweep; strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 2.0 * math.pi  # 6.283185307179586

f = StepFile(
    catalog_id="Gs104",
    defect=(
        "SURFACE_OF_REVOLUTION (profile LINE on Z-axis) IS "
        "ADVANCED_FACE.face_geometry; face boundary on degenerate swept "
        "surface IS the mechanism wired into face topology; "
        "IsDegenerated() cross-product test near-zero not classified singular "
        "IS the defect; shape_null"
    ),
)

# ── SURFACE_OF_REVOLUTION: profile LINE along Z-axis (coincides with axis) ───
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION')
# Profile: line through (0,0,0) in direction (0,0,1) — on the revolution axis.
# Axis of revolution: Z-axis through (0,0,0).
prof_orig = f.cartesian_point((0.0, 0.0, 0.0))
prof_dir  = f.direction((0.0, 0.0, 1.0))
prof_vec  = f.vector(prof_dir, 1.0)
prof_line = f.line(prof_orig, prof_vec)

axis_orig = f.cartesian_point((0.0, 0.0, 0.0))
axis_zdir = f.direction((0.0, 0.0, 1.0))
axis_xdir = f.direction((1.0, 0.0, 0.0))
axis_ax   = f._emit_raw(
    f"AXIS1_PLACEMENT('gs104_axis',#{axis_orig.eid},#{axis_zdir.eid})"
)

sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs104_sor',#{prof_line.eid},#{axis_ax.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: degenerate strip u:[0,2π], v:[0,1] ────────────────────────
# All 3D points are on the Z-axis (radius=0 everywhere due to profile-on-axis).
p_A = f.cartesian_point((0.0, 0.0, 0.0))  # (u=0,   v=0)
p_B = f.cartesian_point((0.0, 0.0, 0.0))  # (u=2π,  v=0)  — same 3D point
p_C = f.cartesian_point((0.0, 0.0, 1.0))  # (u=2π,  v=1)
p_D = f.cartesian_point((0.0, 0.0, 1.0))  # (u=0,   v=1)  — same 3D point

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sor.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom seam A→B (v=0, u: 0→2π) — degenerate, all same 3D point
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.001,
                  (0.0, 0.0), (1.0, 0.0), TWO_PI)
# e1: right seam B→C (u=2π, v: 0→1)
e1 = mk_edge_line(v_B, v_C,
                  (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (TWO_PI, 0.0), (0.0, 1.0), 1.0)
# e2: top seam C→D (v=1, u: 2π→0) — degenerate, all same 3D point
e2 = mk_edge_line(v_C, v_D,
                  (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), 0.001,
                  (TWO_PI, 1.0), (-1.0, 0.0), TWO_PI)
# e3: left seam D→A (u=0, v: 1→0)
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION (profile on axis) IS the face_geometry;
# degenerate swept-surface boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sor)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
