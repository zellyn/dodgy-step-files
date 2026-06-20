"""Gs099 — Sphere pole singularity: iso-curve sampling misses pole.

Catalog claim: ShapeAnalysis_Surface.Singularity() must report both poles of a
sphere, but iso-curve sampling (UIso/VIso) may miss poles if orientation places
them outside parametric trim bounds. Newton iteration on iso-curve sampling
fails to detect singular points at poles.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0, Z-axis) IS the ADVANCED_FACE.face_geometry;
    face boundary trimmed to southern hemisphere only (v: -π/2→0), placing the
    south pole at v=-π/2 exactly at the trim boundary IS the mechanism wired
    into face topology; iso-curve sampling at mid-v misses south-pole singularity
    IS the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE'),
                     contains(b'-1.5707963267948966').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE (radius=1.0) IS the
    ADVANCED_FACE.face_geometry; southern hemisphere trim with south pole at
    v=-1.5707963267948966 (-π/2) exactly at trim boundary IS the mechanism
    wired into face topology; iso-curve sampling misses pole singularity
    outside interior domain IS the defect.
  - shape_null driver: missed pole singularity detection; strict kernels
    reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

NEG_PI_OVER_2 = -math.pi / 2  # -1.5707963267948966

f = StepFile(
    catalog_id="Gs099",
    defect=(
        "SPHERICAL_SURFACE (radius=1.0, Z-axis) IS ADVANCED_FACE.face_geometry; "
        "southern hemisphere trim with south pole at v=-1.5707963267948966 (-π/2) "
        "at trim boundary IS the mechanism wired into face topology; iso-curve "
        "sampling misses south-pole singularity IS the defect; shape_null"
    ),
)

# ── SPHERICAL_SURFACE radius 1, Z-axis vertical ───────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs099_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere   = f._emit_raw(f"SPHERICAL_SURFACE('gs099_sphere',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: southern hemisphere; south pole at v=-π/2 ──────────────────
# Byte assertion: contains(b'-1.5707963267948966')
# 3D corners: equator strip at v=0, south pole at v=-π/2.
# Use wedge: (u=0,v=0)→(u=π,v=0)→south pole.
p_eq0  = f.cartesian_point(( 1.0,  0.0,  0.0))   # (u=0,   v=0)
p_eq1  = f.cartesian_point((-1.0,  0.0,  0.0))   # (u=π,   v=0)
p_south = f.cartesian_point(( 0.0,  0.0, -1.0))  # south pole v=-π/2

v_eq0   = f.vertex_point(p_eq0)
v_eq1   = f.vertex_point(p_eq1)
v_south = f.vertex_point(p_south)

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

# e0: equator arc eq0→eq1 (v=0, u: 0→π)
e0 = mk_edge_line(v_eq0, v_eq1,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (0.0, 0.0), (1.0, 0.0), math.pi)

# e1: meridian eq1→south (u=π, v: 0→-π/2)
# pcurve v reaches -1.5707963267948966 — the south pole singularity
e1 = mk_edge_line(v_eq1, v_south,
                  (-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1.0,
                  (math.pi, 0.0), (0.0, -1.0), abs(NEG_PI_OVER_2))

# e2: degenerate south pole edge (south→south, u: π→0)
p3_sp_degen = f.cartesian_point((0.0, 0.0, -1.0))
d3_sp_degen = f.direction((0.0, 0.0, -1.0))
v3_sp_degen = f.vector(d3_sp_degen, 0.001)
l3_sp_degen = f.line(p3_sp_degen, v3_sp_degen)
# Byte assertion: -1.5707963267948966 appears in pcurve v-coord
p2_sp_degen = f.cartesian_point((math.pi, NEG_PI_OVER_2))
d2_sp_degen = f.direction((-1.0, 0.0))
v2_sp_degen = f.vector(d2_sp_degen, math.pi)
l2_sp_degen = f.line(p2_sp_degen, v2_sp_degen)
pcd_sp = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_sp',(#{l2_sp_degen.eid}),#{prc.eid})")
pc_sp  = f._emit_raw(f"PCURVE('pc_sp',#{sphere.eid},#{pcd_sp.eid})")
sc_sp  = f._emit_raw(f"SURFACE_CURVE('sc_sp',#{l3_sp_degen.eid},(#{pc_sp.eid}),.PCURVE_S1.)")
e2 = f._emit_raw(
    f"EDGE_CURVE('ec_sp_degen',#{v_south.eid},#{v_south.eid},#{sc_sp.eid},.T.)"
)

# e3: meridian south→eq0 (u=0, v: -π/2→0)
e3 = mk_edge_line(v_south, v_eq0,
                  (0.0, 0.0, -1.0), (1.0, 0.0, 1.0), math.sqrt(2),
                  (0.0, NEG_PI_OVER_2), (0.0, 1.0), abs(NEG_PI_OVER_2))

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SPHERICAL_SURFACE IS the face_geometry; south-pole at v=-π/2 trim boundary IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
