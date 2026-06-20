"""Gs146 — SurfaceNewton zero-normal break.

Catalog claim: ShapeAnalysis_Surface::SurfaceNewton() performs iterative
projection of a 3D point onto a surface by evaluating surface normals at
each Newton step. At singular points (sphere pole, cone apex, degenerate
patch), D1 partial derivatives collapse to zero magnitude, and the
subsequent normalization step divides by zero, returning an invalid
(nan/inf) projection result.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 1.0) IS the ADVANCED_FACE.face_geometry;
    face boundary edge crosses the sphere's south pole singularity
    (v = -pi/2), where D1 derivatives collapse to zero magnitude IS the
    mechanism wired into face topology; SurfaceNewton zero-normal
    division-by-zero guard absence IS the defect.
  - Byte assertions: contains(b'SPHERICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    face boundary edge at south-pole singularity (D1=0, zero normal) IS
    the mechanism wired into face topology; SurfaceNewton missing
    normal-magnitude guard IS the defect.
  - shape_null driver: Newton projection returns nan/inf at zero-normal
    singularity; face evaluation fails; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs146",
    defect=(
        "SPHERICAL_SURFACE (radius 1.0) IS ADVANCED_FACE.face_geometry; "
        "face boundary edge at south-pole singularity (v=-pi/2, D1 partial "
        "derivatives collapse to zero magnitude) IS the mechanism wired into "
        "face topology; SurfaceNewton zero-normal division-by-zero guard "
        "absence IS the defect; shape_null"
    ),
)

# ── SPHERICAL_SURFACE ──────────────────────────────────────────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE')
# Radius 1.0. South pole at v = -pi/2: (0, 0, -1).
# At v=-pi/2: dS/du = (0,0,0) and dS/dv = (0,0,0) → D1 magnitude = 0.
# SurfaceNewton iterating toward this point hits division-by-zero in
# normal normalization step.
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs146_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('gs146_sphere',#{sph_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: strip including south pole singularity ─────────────────────
# Spherical parametrization: x=cos(v)*cos(u), y=cos(v)*sin(u), z=sin(v)
# u in [0, pi], v in [-pi/2, -pi/4] — strip from south pole to mid-south.
# The bottom edge runs along v=-pi/2 (south pole): degenerate, zero-length in 3D.
# This edge IS the zero-normal singularity wired into face topology.
TWO_PI = 2.0 * math.pi
u_right = math.pi
v_bot = -math.pi / 2.0  # south pole singularity
v_top = -math.pi / 4.0  # mid-southern hemisphere

def sph_pt(u, v):
    return (math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v))

# At south pole (v=-pi/2): all u map to (0, 0, -1)
sp_3d = sph_pt(0.0, v_bot)   # = (0, 0, -1)

A3 = sph_pt(0.0, v_top)
B3 = sph_pt(u_right, v_top)

p_sp_L = f.cartesian_point(sp_3d)
p_sp_R = f.cartesian_point(sp_3d)
p_A = f.cartesian_point(A3)
p_B = f.cartesian_point(B3)

v_sp_L = f.vertex_point(p_sp_L)
v_sp_R = f.vertex_point(p_sp_R)
v_A    = f.vertex_point(p_A)
v_B    = f.vertex_point(p_B)

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

dv = v_top - v_bot  # positive

# South-pole degenerate edge: sp_L → sp_R, u=0→u_right at v=v_bot (3D: zero-length)
# This IS the zero-normal singularity edge.
e0 = mk_edge_line(v_sp_L, v_sp_R,
                  sp_3d, (1.0, 0.0, 0.0), 1e-6,
                  (0.0, v_bot), (1.0, 0.0), u_right)
# Right: sp_R → B, u=u_right, v=v_bot→v_top
e1 = mk_edge_line(v_sp_R, v_B,
                  sp_3d, (B3[0]-sp_3d[0], B3[1]-sp_3d[1], B3[2]-sp_3d[2]), dv,
                  (u_right, v_bot), (0.0, 1.0), dv)
# Top: B → A, u=u_right→0 at v=v_top
e2 = mk_edge_line(v_B, v_A,
                  B3, (A3[0]-B3[0], A3[1]-B3[1], 0.0), math.cos(v_top) * u_right,
                  (u_right, v_top), (-1.0, 0.0), u_right)
# Left: A → sp_L, u=0, v=v_top→v_bot
e3 = mk_edge_line(v_A, v_sp_L,
                  A3, (-A3[0], -A3[1], sp_3d[2]-A3[2]), dv,
                  (0.0, v_top), (0.0, -1.0), dv)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SPHERICAL_SURFACE IS the face_geometry; south-pole degenerate edge
# (D1=0, zero-normal singularity) IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
