"""Gs060 — Spherical surface pole singularity detection.

Catalog claim: A SPHERICAL_SURFACE (radius 5, ISO axes) has natural poles at
v=π/2 (north) and v=-π/2 (south) where the surface normal becomes degenerate.
ShapeAnalysis_Surface.ComputeSingularities detects the degenerate normals;
edge loops that cross or reach the pole singularity cannot be adjusted, so
the face is rejected or marked degenerate.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 5.0) IS the ADVANCED_FACE.face_geometry; face
    bound edge loop extends to the pole at v=π/2 (north pole, where surface
    normal is degenerate) IS the defect wired into face topology.
  - Byte assertions: contains(b'SPHERICAL_SURFACE'),
                     contains(b'1.5707963267948966').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    edge loop reaching v=1.5707963267948966 (north pole, π/2) IS the defect
    wired into face topology; normal degenerates at the pole to zero-length.
  - shape_null driver: ComputeSingularities detects pole; edge loop
    adjustment fails; strict kernels produce empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs060",
    defect=(
        "SPHERICAL_SURFACE (radius 5.0) IS ADVANCED_FACE.face_geometry; "
        "edge loop reaching v=1.5707963267948966 (north pole, π/2) IS the defect; "
        "degenerate normal at pole IS wired into face topology; "
        "shape_null (ComputeSingularities detects pole, strict reject)"
    ),
)

# ── SPHERICAL_SURFACE radius 5, Z-axis vertical ───────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs060_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere   = f._emit_raw(f"SPHERICAL_SURFACE('gs060_sphere',#{sph_ax.eid},5.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: a wedge that reaches the north pole (v=π/2) ───────────────
# North pole in 3D: (0, 0, 5). Corner A and D are at v=π/2 (degenerate point).
# Byte assertion: contains(b'1.5707963267948966')
PI_OVER_2 = math.pi / 2  # = 1.5707963267948966

# 3D corners
# Equator points at v=0, u=0 and u=π/2
p_B = f.cartesian_point(( 5.0,  0.0,  0.0))   # (u=0,   v=0)
p_C = f.cartesian_point(( 0.0,  5.0,  0.0))   # (u=π/2, v=0)
# North pole (degenerate) — both A and D land here
p_pole = f.cartesian_point(( 0.0,  0.0,  5.0))  # (u=any, v=π/2)

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

# e0: equator arc B→C (v=0, u 0→π/2)
e0 = mk_edge_line(v_B, v_C,
                  (5.0, 0.0, 0.0), (-5.0, 5.0, 0.0), 5.0*math.sqrt(2),
                  (0.0, 0.0), (1.0, 0.0), PI_OVER_2)

# e1: meridian C→pole (u=π/2, v 0→π/2)
# pcurve v reaches 1.5707963267948966 — the degenerate pole parameter
e1 = mk_edge_line(v_C, v_pole,
                  (0.0, 5.0, 0.0), (0.0, -5.0, 5.0), 5.0*math.sqrt(2),
                  (PI_OVER_2, 0.0), (0.0, 1.0), PI_OVER_2)

# e2: degenerate edge at north pole (pole→pole, u from π/2 to 0) — zero-length
# The pcurve holds v=1.5707963267948966 — the pole singularity
p3_degen = f.cartesian_point((0.0, 0.0, 5.0))
d3_degen = f.direction((0.0, 0.0, 1.0))
v3_degen = f.vector(d3_degen, 0.001)
l3_degen = f.line(p3_degen, v3_degen)
# pcurve at v=π/2 (degenerate): u sweeps π/2→0
p2_degen = f.cartesian_point((PI_OVER_2, 1.5707963267948966))
d2_degen = f.direction((-1.0, 0.0))
v2_degen = f.vector(d2_degen, PI_OVER_2)
l2_degen = f.line(p2_degen, v2_degen)
pcd_degen= f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_degen',(#{l2_degen.eid}),#{prc.eid})")
pc_degen = f._emit_raw(f"PCURVE('pc_degen',#{sphere.eid},#{pcd_degen.eid})")
sc_degen = f._emit_raw(f"SURFACE_CURVE('sc_degen',#{l3_degen.eid},(#{pc_degen.eid}),.PCURVE_S1.)")
e2 = f._emit_raw(
    f"EDGE_CURVE('ec_degen',#{v_pole.eid},#{v_pole.eid},#{sc_degen.eid},.T.)"
)

# e3: meridian pole→B (u=0, v π/2→0)
e3 = mk_edge_line(v_pole, v_B,
                  (0.0, 0.0, 5.0), (5.0, 0.0, -5.0), 5.0*math.sqrt(2),
                  (0.0, PI_OVER_2), (0.0, -1.0), PI_OVER_2)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SPHERICAL_SURFACE IS the face_geometry; pole singularity IS the face surface defect.
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
