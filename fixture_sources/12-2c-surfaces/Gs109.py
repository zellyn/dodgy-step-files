"""Gs109 — ShapeAnalysis_Surface.UVFromIso v-iso-at-pole.

Catalog claim: ShapeAnalysis_Surface::UVFromIso parameter test allows u-iso at
v=pole of sphere even though u is undefined at the pole; parameter is accepted
but produces meaningless results.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0) IS the ADVANCED_FACE.face_geometry; face
    boundary includes a degenerate edge at v=π/2 (north pole) where u is
    undefined — the face encodes a u-iso extracted at v=π/2 as a non-degenerate
    pcurve IS the mechanism wired into face topology; UVFromIso accepts the
    pole-u parameter and returns meaningless UV IS the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE (radius=1.0) IS the
    ADVANCED_FACE.face_geometry; face boundary pcurve at v=π/2 pole
    (where u is undefined) encoded as non-degenerate edge IS the mechanism
    wired into face topology; UVFromIso accepts meaningless pole-u parameter
    IS the defect.
  - shape_null driver: u-iso at pole is geometrically undefined; strict kernels
    reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

HALF_PI = math.pi / 2.0   # 1.5707963267948966
TWO_PI  = 2.0 * math.pi   # 6.283185307179586

f = StepFile(
    catalog_id="Gs109",
    defect=(
        "SPHERICAL_SURFACE (radius=1.0) IS ADVANCED_FACE.face_geometry; "
        "face boundary pcurve at v=1.5707963267948966 pole (where u is undefined) "
        "encoded as non-degenerate edge IS the mechanism wired into face topology; "
        "UVFromIso accepts meaningless pole-u parameter IS the defect; shape_null"
    ),
)

# ── SPHERICAL_SURFACE radius 1.0 ──────────────────────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs109_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sph = f._emit_raw(f"SPHERICAL_SURFACE('gs109_sph',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: hemisphere patch u:[0,2π], v:[0,π/2] ──────────────────────
# The top edge at v=π/2 is the mechanism: a pcurve at the north pole
# representing a u-iso where u is actually undefined.
# 3D corners:
#   A: (1,0,0) at (u=0,   v=0)       equator
#   B: (1,0,0) at (u=2π,  v=0)       same 3D (seam)
#   C: (0,0,1) at (u=π/2, v=π/2)     north pole (arbitrary u)
#   D: (0,0,1) at (u=0,   v=π/2)     north pole (u=0)
p_A = f.cartesian_point((1.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))   # seam: same 3D as A
p_C = f.cartesian_point((0.0, 0.0, 1.0))   # north pole (u=π/2)
p_D = f.cartesian_point((0.0, 0.0, 1.0))   # north pole (u=0)

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

# e0: equator A→B (v=0, u: 0→2π)
e0 = mk_edge_line(v_A, v_B,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.001,
                  (0.0, 0.0), (1.0, 0.0), TWO_PI)
# e1: seam meridian B→C (u=2π, v: 0→π/2) — rises to north pole
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 1.0), HALF_PI,
                  (TWO_PI, 0.0), (0.0, 1.0), HALF_PI)
# e2: pole edge C→D (v=π/2, u: π/2→0) — u-iso at north pole; u is undefined here.
# Non-degenerate pcurve at pole is THE MECHANISM; UVFromIso accepts it but
# produces meaningless result.
e2 = mk_edge_line(v_C, v_D,
                  (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.001,
                  (HALF_PI, HALF_PI), (-1.0, 0.0), HALF_PI)
# e3: meridian D→A (u=0, v: π/2→0) — descends from north pole
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
# non-degenerate pcurve at v=π/2 pole (u undefined) IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sph)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
