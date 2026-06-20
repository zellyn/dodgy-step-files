"""Gs101 — ShapeAnalysis_Surface.ValueOfUV: antipodal sphere convergence failure.

Catalog claim: ValueOfUV() projects a 3D point onto a sphere using Newton
iteration seeded from initial UV guess. When target is near the antipode of
the seed, Newton initializes on the wrong sheet and converges to wrong root.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0, Z-axis) IS the ADVANCED_FACE.face_geometry;
    face boundary edge loop contains an edge whose 3D vertex sits at the
    antipode of the default UV seed — specifically the point (0,0,-1) (south
    pole, UV=(π,-π/2)) with seed at north-pole region (UV=(0,π/2)) IS the
    mechanism wired into face topology; ValueOfUV Newton iteration initialised
    at north pole converges to wrong root when projecting south-pole point
    IS the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE'),
                     contains(b'-1.5707963267948966').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE (radius=1.0) IS the
    ADVANCED_FACE.face_geometry; antipodal south-pole vertex at (0,0,-1)
    (v=-1.5707963267948966) IS the mechanism wired into face topology;
    ValueOfUV Newton seed at north pole converges to wrong antipodal root
    IS the defect.
  - shape_null driver: wrong-root projection failure; strict kernels reject;
    empty result.
"""
import math
from step_corpus.step_builder import StepFile

NEG_PI_OVER_2 = -math.pi / 2  # -1.5707963267948966

f = StepFile(
    catalog_id="Gs101",
    defect=(
        "SPHERICAL_SURFACE (radius=1.0, Z-axis) IS ADVANCED_FACE.face_geometry; "
        "antipodal south-pole vertex at (0,0,-1) with v=-1.5707963267948966 "
        "IS the mechanism wired into face topology; ValueOfUV Newton iteration "
        "seeded at north-pole region converges to wrong antipodal root "
        "IS the defect; shape_null"
    ),
)

# ── SPHERICAL_SURFACE radius 1, Z-axis vertical ───────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs101_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere   = f._emit_raw(f"SPHERICAL_SURFACE('gs101_sphere',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: great-circle arc including antipodal south-pole vertex ──────
# Byte assertion: contains(b'-1.5707963267948966')
# North equator point: (1,0,0) at (u=0, v=0) — seed region for Newton
# South pole: (0,0,-1) at (u=0, v=-π/2) — antipodal target
p_north_eq = f.cartesian_point((1.0, 0.0,  0.0))   # (u=0,   v=0)
p_south    = f.cartesian_point((0.0, 0.0, -1.0))   # south pole v=-π/2

v_north_eq = f.vertex_point(p_north_eq)
v_south    = f.vertex_point(p_south)

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

# e0: equator arc at v=0, u: 0→π (north_eq → opposite equator)
p_opp_eq   = f.cartesian_point((-1.0, 0.0, 0.0))  # (u=π, v=0)
v_opp_eq   = f.vertex_point(p_opp_eq)

e0 = mk_edge_line(v_north_eq, v_opp_eq,
                  (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (0.0, 0.0), (1.0, 0.0), math.pi)

# e1: meridian opp_eq → south (u=π, v: 0 → -π/2)
# pcurve v reaches -1.5707963267948966 — antipodal south pole
e1 = mk_edge_line(v_opp_eq, v_south,
                  (-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1.0,
                  (math.pi, 0.0), (0.0, -1.0), abs(NEG_PI_OVER_2))

# e2: degenerate south-pole edge (south→south, u: π→0)
# Byte assertion: -1.5707963267948966 appears in pcurve start v
p3_s_degen = f.cartesian_point((0.0, 0.0, -1.0))
d3_s_degen = f.direction((0.0, 0.0, -1.0))
v3_s_degen = f.vector(d3_s_degen, 0.001)
l3_s_degen = f.line(p3_s_degen, v3_s_degen)
p2_s_degen = f.cartesian_point((math.pi, NEG_PI_OVER_2))
d2_s_degen = f.direction((-1.0, 0.0))
v2_s_degen = f.vector(d2_s_degen, math.pi)
l2_s_degen = f.line(p2_s_degen, v2_s_degen)
pcd_s = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_s',(#{l2_s_degen.eid}),#{prc.eid})")
pc_s  = f._emit_raw(f"PCURVE('pc_s',#{sphere.eid},#{pcd_s.eid})")
sc_s  = f._emit_raw(f"SURFACE_CURVE('sc_s',#{l3_s_degen.eid},(#{pc_s.eid}),.PCURVE_S1.)")
e2 = f._emit_raw(
    f"EDGE_CURVE('ec_s_degen',#{v_south.eid},#{v_south.eid},#{sc_s.eid},.T.)"
)

# e3: meridian south → north_eq (u=0, v: -π/2 → 0) — closes the loop
e3 = mk_edge_line(v_south, v_north_eq,
                  (0.0, 0.0, -1.0), (1.0, 0.0, 1.0), math.sqrt(2),
                  (0.0, NEG_PI_OVER_2), (0.0, 1.0), abs(NEG_PI_OVER_2))

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SPHERICAL_SURFACE IS the face_geometry; antipodal south-pole vertex IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
