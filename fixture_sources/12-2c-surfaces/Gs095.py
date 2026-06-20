"""Gs095 — ShapeUpgrade_ConvertSurfaceToBezierBasis sphere.

Catalog claim: SPHERICAL_SURFACE conversion to Bezier basis produces 4 patches,
but pole regions become degenerate Bezier patches with zero-area. Control points
collapse at poles, violating Bezier non-degeneracy.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0, Z-axis pole) IS the ADVANCED_FACE.face_geometry;
    face boundary edge loop reaches the north pole (v=π/2) — zero-area pole
    patch IS the mechanism wired into face topology; ConvertSurfaceToBezierBasis
    produces degenerate Bezier patches at poles (control points collapse) IS
    the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE'),
                     contains(b'1.5707963267948966').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE (radius=1.0) IS the
    ADVANCED_FACE.face_geometry; edge loop reaching north pole v=π/2
    (v=1.5707963267948966) IS the mechanism wired into face topology;
    ConvertSurfaceToBezierBasis collapses control points at pole, producing
    zero-area degenerate Bezier patch IS the defect.
  - shape_null driver: degenerate Bezier patch at pole; strict kernels
    reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs095",
    defect=(
        "SPHERICAL_SURFACE (radius=1.0) IS ADVANCED_FACE.face_geometry; "
        "edge loop reaching north pole v=1.5707963267948966 (π/2) IS the "
        "mechanism wired into face topology; ConvertSurfaceToBezierBasis "
        "collapses control points at pole, producing degenerate zero-area "
        "Bezier patch IS the defect; shape_null"
    ),
)

# ── SPHERICAL_SURFACE radius 1, Z-axis vertical ───────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs095_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere   = f._emit_raw(f"SPHERICAL_SURFACE('gs095_sphere',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: wedge reaching the north pole (v=π/2) ─────────────────────
# Byte assertion: contains(b'1.5707963267948966')
PI_OVER_2 = math.pi / 2  # = 1.5707963267948966

# 3D corners
p_B    = f.cartesian_point(( 1.0,  0.0,  0.0))   # (u=0,   v=0) — equator
p_C    = f.cartesian_point(( 0.0,  1.0,  0.0))   # (u=π/2, v=0) — equator
p_pole = f.cartesian_point(( 0.0,  0.0,  1.0))   # north pole (v=π/2, degenerate)

v_B    = f.vertex_point(p_B)
v_C    = f.vertex_point(p_C)
v_pole = f.vertex_point(p_pole)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sphere.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: equator arc B→C (v=0, u: 0→π/2)
e0 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (-1.0, 1.0, 0.0), math.sqrt(2),
                  (0.0, 0.0), (1.0, 0.0), PI_OVER_2)

# e1: meridian C→pole (u=π/2, v: 0→π/2)
# pcurve v reaches 1.5707963267948966 — the degenerate pole parameter
e1 = mk_edge_line(v_C, v_pole,
                  (0.0, 1.0, 0.0), (0.0, -1.0, 1.0), math.sqrt(2),
                  (PI_OVER_2, 0.0), (0.0, 1.0), PI_OVER_2)

# e2: degenerate edge at north pole (pole→pole) — zero-length in 3D
# pcurve stays at v=1.5707963267948966, u sweeps π/2→0 — the pole collapse
p3_degen = f.cartesian_point((0.0, 0.0, 1.0))
d3_degen = f.direction((0.0, 0.0, 1.0))
v3_degen = f.vector(d3_degen, 0.001)
l3_degen = f.line(p3_degen, v3_degen)
p2_degen = f.cartesian_point((PI_OVER_2, 1.5707963267948966))
d2_degen = f.direction((-1.0, 0.0))
v2_degen = f.vector(d2_degen, PI_OVER_2)
l2_degen = f.line(p2_degen, v2_degen)
pcd_degen = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_degen',(#{l2_degen.eid}),#{prc.eid})")
pc_degen  = f._emit_raw(f"PCURVE('pc_degen',#{sphere.eid},#{pcd_degen.eid})")
sc_degen  = f._emit_raw(f"SURFACE_CURVE('sc_degen',#{l3_degen.eid},(#{pc_degen.eid}),.PCURVE_S1.)")
e2 = f._emit_raw(
    f"EDGE_CURVE('ec_degen',#{v_pole.eid},#{v_pole.eid},#{sc_degen.eid},.T.)"
)

# e3: meridian pole→B (u=0, v: π/2→0)
e3 = mk_edge_line(v_pole, v_B,
                  (0.0, 0.0, 1.0), (1.0, 0.0, -1.0), math.sqrt(2),
                  (0.0, PI_OVER_2), (0.0, -1.0), PI_OVER_2)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SPHERICAL_SURFACE IS the face_geometry; pole collapse (v=π/2) IS the mechanism wired into face.
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
