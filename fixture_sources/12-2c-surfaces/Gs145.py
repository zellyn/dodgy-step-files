"""Gs145 — ProjectDegenerated lazy singularity init.

Catalog claim: ShapeAnalysis_Surface::ProjectDegenerated() assumes
singularities have already been initialized (myNbDeg >= 0). When called
on a freshly-constructed surface with stale state (myNbDeg < 0),
the lazy recomputation path is skipped, so ComputeSingularities is never
triggered. Degenerate edges then project to incorrect u/v values rather
than the true singularity locus (cone apex, sphere pole).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE (semi-angle pi/6, radius 0.0 at apex) IS the
    ADVANCED_FACE.face_geometry; the degenerate edge at the cone apex
    (all u values map to the single apex point) IS the mechanism wired
    into face topology; ProjectDegenerated lazy singularity init (myNbDeg<0
    guard skipped) IS the defect.
  - Byte assertions: contains(b'CONICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    degenerate apex edge (singularity locus at v=0) IS the mechanism wired
    into face topology; ProjectDegenerated myNbDeg<0 lazy-init skip IS the
    defect.
  - shape_null driver: degenerate edge projects to wrong u/v; topology
    invalid; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs145",
    defect=(
        "CONICAL_SURFACE (apex singularity at v=0, semi-angle pi/6) "
        "IS ADVANCED_FACE.face_geometry; degenerate apex edge (singularity "
        "locus where all u values converge to apex) IS the mechanism wired "
        "into face topology; ProjectDegenerated lazy singularity init "
        "(myNbDeg<0 guard skipped) IS the defect; shape_null"
    ),
)

# ── CONICAL_SURFACE with apex at origin ────────────────────────────────────────
# Byte assertion: contains(b'CONICAL_SURFACE')
# semi_angle = pi/6 (30 degrees). At v=0 this is the apex: all u values
# map to (0,0,0). This is the singularity locus that ProjectDegenerated
# must project onto — but lazy-init skip sends edges to wrong u/v.
HALF_ANGLE = math.pi / 6.0
TWO_PI = 2.0 * math.pi

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs145_cone_ax',#{cone_orig.eid},#{cone_zdir.eid},#{cone_xdir.eid})"
)
# CONICAL_SURFACE(name, axis, radius_at_position=0.0, semi_angle)
cone = f._emit_raw(f"CONICAL_SURFACE('gs145_cone',#{cone_ax.eid},0.0,{HALF_ANGLE:.10f})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: apex edge + lateral strip ───────────────────────────────────
# CONICAL_SURFACE parametrization: x = v*cos(u)*cos(ha), y = v*sin(u)*cos(ha),
# z = v*sin(ha), half-angle ha=pi/6.
# Apex singularity at v=0: all u values collapse to (0,0,0).
# Face: v in [0, 1.5] (includes apex), u in [0, 2pi/3] (partial U sweep).
# The bottom edge is the degenerate apex edge (both vertices at v=0 apex).
cos_ha = math.cos(HALF_ANGLE)
sin_ha = math.sin(HALF_ANGLE)
v_top = 1.5
u_right = TWO_PI / 3.0

def cone_pt(u, v):
    return (v * math.cos(u) * cos_ha, v * math.sin(u) * cos_ha, v * sin_ha)

# Apex (degenerate): all u collapse here
apex_3d = cone_pt(0.0, 0.0)   # = (0,0,0)
# Top corners
C3 = cone_pt(0.0, v_top)
D3 = cone_pt(u_right, v_top)

p_apex_L = f.cartesian_point(apex_3d)
p_apex_R = f.cartesian_point(apex_3d)  # same 3D point — degenerate edge
p_C = f.cartesian_point(C3)
p_D = f.cartesian_point(D3)

v_apex_L = f.vertex_point(p_apex_L)
v_apex_R = f.vertex_point(p_apex_R)
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
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Degenerate apex edge: apex_L → apex_R, u=0→u_right at v=0 (null 3D movement)
# This IS the singularity locus that ProjectDegenerated must handle.
e0 = mk_edge_line(v_apex_L, v_apex_R,
                  apex_3d, (1.0, 0.0, 0.0), 1e-6,
                  (0.0, 0.0), (1.0, 0.0), u_right)
# Right lateral: apex_R → C, u=u_right, v=0→v_top
e1 = mk_edge_line(v_apex_R, v_D,
                  apex_3d, (D3[0]-apex_3d[0], D3[1]-apex_3d[1], D3[2]-apex_3d[2]), v_top,
                  (u_right, 0.0), (0.0, 1.0), v_top)
# Top: D → C, u=u_right→0 at v=v_top
e2 = mk_edge_line(v_D, v_C,
                  D3, (C3[0]-D3[0], C3[1]-D3[1], C3[2]-D3[2]), v_top * u_right * cos_ha,
                  (u_right, v_top), (-1.0, 0.0), u_right)
# Left lateral: C → apex_L, u=0, v=v_top→0
e3 = mk_edge_line(v_C, v_apex_L,
                  C3, (-C3[0], -C3[1], -C3[2]), v_top,
                  (0.0, v_top), (0.0, -1.0), v_top)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CONICAL_SURFACE IS the face_geometry; degenerate apex edge (singularity
# locus at v=0) IS the mechanism wired into face topology — exercises
# ProjectDegenerated lazy-singularity-init bug at runtime.
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
