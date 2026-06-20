"""Gs174 — SphericalSurface Pole Singularities.

Catalog claim: ShapeAnalysis_Surface.ComputeSingularities fails to detect
both north and south poles when singularities are cached after the first
pole is found. Sphere (radius 1.0); both V-closed vertex loops present.
Healing detects dual poles; without fix myUIsoDeg=false at each pole.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0) IS the ADVANCED_FACE.face_geometry;
    face boundary includes both a north-pole degenerate loop (v=+π/2) and a
    south-pole degenerate loop (v=-π/2) IS the mechanism wired into face
    topology; ShapeAnalysis_Surface.ComputeSingularities caching singularities
    after first pole (myUIsoDeg left false at second pole) IS the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE (radius=1.0) IS
    ADVANCED_FACE.face_geometry; face boundary with both north-pole degenerate
    loop (v=+π/2) and south-pole degenerate loop (v=-π/2) IS the mechanism
    wired into face topology; ShapeAnalysis_Surface.ComputeSingularities
    caching after first pole (myUIsoDeg=false at second pole) IS the defect.
  - shape_null driver: missed second pole singularity (myUIsoDeg=false) causes
    UV loop adjustment to fail at south pole; strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs174",
    defect=(
        "SPHERICAL_SURFACE (radius=1.0) IS ADVANCED_FACE.face_geometry; "
        "face boundary with both north-pole degenerate loop (v=+π/2) and "
        "south-pole degenerate loop (v=-π/2) IS the mechanism wired into face "
        "topology; ShapeAnalysis_Surface.ComputeSingularities caching after "
        "first pole (myUIsoDeg=false at second pole, dual-pole detection miss) "
        "IS the defect; shape_null"
    ),
)

# ── SPHERICAL_SURFACE radius 1.0, Z-axis vertical ────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
#
# A sphere of radius 1.0 has:
#   North pole: v = +π/2 = +1.5707963267948966  (3D: (0,0,+1))
#   South pole: v = -π/2 = -1.5707963267948966  (3D: (0,0,-1))
#
# ShapeAnalysis_Surface.ComputeSingularities detects singularities by
# checking each V-iso line. A caching bug causes the computation to stop
# after the first pole is cached; the second pole is skipped, leaving
# myUIsoDeg=false there. This fixture provides a complete sphere boundary
# that touches BOTH poles, triggering the dual-pole cache failure.

PI_OVER_2 = math.pi / 2  # 1.5707963267948966

sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs174_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere   = f._emit_raw(f"SPHERICAL_SURFACE('gs174_sphere',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── 3D key points ─────────────────────────────────────────────────────────────
# Equator: v=0, u=0 and u=π/2
p_eq0    = f.cartesian_point(( 1.0,  0.0,  0.0))   # u=0,    v=0
p_eq90   = f.cartesian_point(( 0.0,  1.0,  0.0))   # u=π/2,  v=0
# North pole: v=+π/2
p_north  = f.cartesian_point(( 0.0,  0.0,  1.0))
# South pole: v=-π/2
p_south  = f.cartesian_point(( 0.0,  0.0, -1.0))

v_eq0   = f.vertex_point(p_eq0)
v_eq90  = f.vertex_point(p_eq90)
v_north = f.vertex_point(p_north)
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


# ── Outer bound: quadrant touching north pole ─────────────────────────────────
# Equator edge: eq0 → eq90, v=0, u: 0→π/2
e_eq = mk_edge_line(v_eq0, v_eq90,
                    (1.0, 0.0, 0.0), (-1.0, 1.0, 0.0), math.sqrt(2.0),
                    (0.0, 0.0), (1.0, 0.0), PI_OVER_2)

# Meridian u=π/2: eq90 → north, v: 0→+π/2
e_mn = mk_edge_line(v_eq90, v_north,
                    (0.0, 1.0, 0.0), (0.0, -1.0, 1.0), math.sqrt(2.0),
                    (PI_OVER_2, 0.0), (0.0, 1.0), PI_OVER_2)

# North pole degenerate edge: north→north, u: π/2→0
p3_ndeg = f.cartesian_point((0.0, 0.0, 1.0))
d3_ndeg = f.direction((0.0, 0.0, 1.0))
v3_ndeg = f.vector(d3_ndeg, 0.001)
l3_ndeg = f.line(p3_ndeg, v3_ndeg)
p2_ndeg = f.cartesian_point((PI_OVER_2,  PI_OVER_2))
d2_ndeg = f.direction((-1.0, 0.0))
v2_ndeg = f.vector(d2_ndeg, PI_OVER_2)
l2_ndeg = f.line(p2_ndeg, v2_ndeg)
pcd_ndeg = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_ndeg',(#{l2_ndeg.eid}),#{prc.eid})")
pc_ndeg  = f._emit_raw(f"PCURVE('pc_ndeg',#{sphere.eid},#{pcd_ndeg.eid})")
sc_ndeg  = f._emit_raw(f"SURFACE_CURVE('sc_ndeg',#{l3_ndeg.eid},(#{pc_ndeg.eid}),.PCURVE_S1.)")
e_ndeg   = f._emit_raw(
    f"EDGE_CURVE('ec_ndeg',#{v_north.eid},#{v_north.eid},#{sc_ndeg.eid},.T.)"
)

# Meridian u=0: north → eq0, v: +π/2→0
e_ms = mk_edge_line(v_north, v_eq0,
                    (0.0, 0.0, 1.0), (1.0, 0.0, -1.0), math.sqrt(2.0),
                    (0.0, PI_OVER_2), (0.0, -1.0), PI_OVER_2)

outer_loop = f.edge_loop([
    f.oriented_edge(e_eq,   True),
    f.oriented_edge(e_mn,   True),
    f.oriented_edge(e_ndeg, True),
    f.oriented_edge(e_ms,   True),
])

# ── Inner bound: quadrant touching south pole ─────────────────────────────────
# Re-use same equator vertices; inner bound runs below equator (v: 0→-π/2).
# Meridian u=0: eq0 → south, v: 0→-π/2
e_ms_s = mk_edge_line(v_eq0, v_south,
                      (1.0, 0.0, 0.0), (-1.0, 0.0, -1.0), math.sqrt(2.0),
                      (0.0, 0.0), (0.0, -1.0), PI_OVER_2)

# South pole degenerate edge: south→south, u: 0→π/2
p3_sdeg = f.cartesian_point((0.0, 0.0, -1.0))
d3_sdeg = f.direction((0.0, 0.0, -1.0))
v3_sdeg = f.vector(d3_sdeg, 0.001)
l3_sdeg = f.line(p3_sdeg, v3_sdeg)
p2_sdeg = f.cartesian_point((0.0, -PI_OVER_2))
d2_sdeg = f.direction((1.0, 0.0))
v2_sdeg = f.vector(d2_sdeg, PI_OVER_2)
l2_sdeg = f.line(p2_sdeg, v2_sdeg)
pcd_sdeg = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_sdeg',(#{l2_sdeg.eid}),#{prc.eid})")
pc_sdeg  = f._emit_raw(f"PCURVE('pc_sdeg',#{sphere.eid},#{pcd_sdeg.eid})")
sc_sdeg  = f._emit_raw(f"SURFACE_CURVE('sc_sdeg',#{l3_sdeg.eid},(#{pc_sdeg.eid}),.PCURVE_S1.)")
e_sdeg   = f._emit_raw(
    f"EDGE_CURVE('ec_sdeg',#{v_south.eid},#{v_south.eid},#{sc_sdeg.eid},.T.)"
)

# Meridian u=π/2: south → eq90, v: -π/2→0
e_ms2 = mk_edge_line(v_south, v_eq90,
                     (0.0, 0.0, -1.0), (0.0, 1.0, 1.0), math.sqrt(2.0),
                     (PI_OVER_2, -PI_OVER_2), (0.0, 1.0), PI_OVER_2)

# Equator back: eq90 → eq0, v=0, u: π/2→0
e_eq_back = mk_edge_line(v_eq90, v_eq0,
                         (0.0, 1.0, 0.0), (1.0, -1.0, 0.0), math.sqrt(2.0),
                         (PI_OVER_2, 0.0), (-1.0, 0.0), PI_OVER_2)

inner_loop = f.edge_loop([
    f.oriented_edge(e_ms_s,   True),
    f.oriented_edge(e_sdeg,   True),
    f.oriented_edge(e_ms2,    True),
    f.oriented_edge(e_eq_back, True),
])

# SPHERICAL_SURFACE (radius=1.0) IS the face_geometry; face boundary with
# both north-pole degenerate loop (v=+π/2) and south-pole degenerate loop
# (v=-π/2) IS the mechanism wired into face topology — exercises
# ShapeAnalysis_Surface.ComputeSingularities caching after first pole
# (myUIsoDeg=false at second pole, dual-pole detection miss).
face  = f.advanced_face(
    [f.face_outer_bound(outer_loop), f.face_bound(inner_loop, True)],
    sphere
)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
