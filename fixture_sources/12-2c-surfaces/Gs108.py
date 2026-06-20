"""Gs108 — Singularity boundary classification error.

Catalog claim: ShapeAnalysis_Surface.Singularity fails to classify singularities
at parameter boundaries. When singularity occurs at v=v_max (inclusive boundary),
the analyzer treats the boundary as exclusive, misclassifying interior vs.
boundary singularities.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0) IS the ADVANCED_FACE.face_geometry; face
    boundary loop reaches v=π/2 (north-pole singularity at v_max) with an
    edge that collapses to a point at v=π/2 IS the mechanism wired into face
    topology; ShapeAnalysis_Surface.Singularity treats v_max boundary as
    exclusive, misclassifying the pole as interior IS the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE (radius=1.0) IS the
    ADVANCED_FACE.face_geometry; face boundary edge degenerating at
    v=π/2 (north pole, v_max) IS the mechanism wired into face topology;
    Singularity() misclassifies inclusive v_max boundary as exclusive IS the defect.
  - shape_null driver: pole-edge at v_max misclassified; strict kernels
    reject degenerate face; empty result.
"""
import math
from step_corpus.step_builder import StepFile

HALF_PI = math.pi / 2.0   # 1.5707963267948966
TWO_PI  = 2.0 * math.pi   # 6.283185307179586

f = StepFile(
    catalog_id="Gs108",
    defect=(
        "SPHERICAL_SURFACE (radius=1.0) IS ADVANCED_FACE.face_geometry; "
        "face boundary edge degenerating at v=1.5707963267948966 (north pole, v_max) "
        "IS the mechanism wired into face topology; "
        "Singularity() misclassifies inclusive v_max boundary as exclusive IS the defect; "
        "shape_null"
    ),
)

# ── SPHERICAL_SURFACE radius 1.0 ──────────────────────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs108_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sph = f._emit_raw(f"SPHERICAL_SURFACE('gs108_sph',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: quarter-sphere patch u:[0,2π], v:[0,π/2] ──────────────────
# The v=π/2 (north-pole) boundary is singular — all u values map to same 3D point.
# 3D corners:
#   A: (1,0,0)  at (u=0,    v=0)     equator, x-axis
#   B: (1,0,0)  at (u=2π,   v=0)     same 3D (seam at u=0/2π)
#   C: (0,0,1)  at (u=2π,   v=π/2)   north pole (degenerate end)
#   D: (0,0,1)  at (u=0,    v=π/2)   north pole (degenerate start)
p_A = f.cartesian_point((1.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))   # seam: same 3D as A
p_C = f.cartesian_point((0.0, 0.0, 1.0))   # north pole
p_D = f.cartesian_point((0.0, 0.0, 1.0))   # north pole: same as C

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sph.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: equator A→B (v=0, u: 0→2π) — full equatorial arc; 3D length ≈ 2π (radius=1)
e0 = mk_edge_line(v_A, v_B,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.001,
                  (0.0, 0.0), (1.0, 0.0), TWO_PI)
# e1: seam B→C (u=2π, v: 0→π/2) — meridian at u=2π rising to north pole
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 1.0), HALF_PI,
                  (TWO_PI, 0.0), (0.0, 1.0), HALF_PI)
# e2: pole edge C→D (v=π/2, u: 2π→0) — degenerate top edge at north pole
# (all 3D points = (0,0,1)); this is the mechanism: boundary at v_max = π/2
e2 = mk_edge_line(v_C, v_D,
                  (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.001,
                  (TWO_PI, HALF_PI), (-1.0, 0.0), TWO_PI)
# e3: seam D→A (u=0, v: π/2→0) — meridian at u=0 descending from north pole
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 1.0), (1.0, 0.0, -1.0), HALF_PI,
                  (0.0, HALF_PI), (0.0, -1.0), HALF_PI)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SPHERICAL_SURFACE IS the face_geometry;
# degenerate pole edge at v=π/2 (v_max) IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sph)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
