"""Gs128 — TOROIDAL_SURFACE with v-closed property and u-iso wraparound.

Catalog claim: ShapeAnalysis_Surface.UVFromIso misclassifies wraparound
handling for u-iso requests on v-closed surfaces. When requesting
u-iso near v=v_max on a v-closed torus, the method confuses u-iso
with v-iso and produces incorrect parameter projection.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE IS the ADVANCED_FACE.face_geometry; face outer bound
    edge pcurve lies along u=u_max (u-iso line) at v near v_max on the
    v-closed surface IS the mechanism wired into face topology;
    UVFromIso u/v-iso confusion on v-closed torus IS the defect.
  - Byte assertions: contains(b'TOROIDAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry;
    face edge pcurve on u-iso line near v=2π (v-closed seam) IS the
    mechanism wired into face topology; UVFromIso u/v-iso misclassification
    IS the defect.
  - shape_null driver: incorrect parameter projection corrupts surface
    reference; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs128",
    defect=(
        "TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "face edge pcurve on u-iso line at v near v_max=2π (v-closed seam) "
        "IS the mechanism wired into face topology; "
        "UVFromIso u/v-iso misclassification on v-closed torus IS the defect; "
        "shape_null"
    ),
)

# ── TOROIDAL_SURFACE ───────────────────────────────────────────────────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
# Major radius R=2, minor radius r=0.5
# Torus axis along Z; v-closed at v=0=2π
torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_zdir = f.direction((0.0, 0.0, 1.0))
torus_xdir = f.direction((1.0, 0.0, 0.0))
torus_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs128_torus_ax',#{torus_orig.eid},#{torus_zdir.eid},#{torus_xdir.eid})"
)
# TOROIDAL_SURFACE(name, axis, major_radius, minor_radius)
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs128_torus',#{torus_ax.eid},2.0,0.5)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: thin strip near the v-seam in parameter space ──────────────
# Parameter domain: u ∈ [0, 2π], v ∈ [0, 2π]
# The face is a narrow band at v near v_max: v ∈ [6.0, 6.28 ≈ 2π]
# One edge is the u-iso line at u=0 running v=6.0→6.28; this is the mechanism:
# UVFromIso is called for u-iso near the v-seam and misclassifies it as v-iso.
#
# 3D points on torus: parametric → Cartesian
# (u,v): x=(R+r*cos(v))*cos(u), y=(R+r*cos(v))*sin(u), z=r*sin(v)
R, r = 2.0, 0.5
TWO_PI = 2.0 * math.pi

def torus_pt(u, v):
    x = (R + r * math.cos(v)) * math.cos(u)
    y = (R + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    return (x, y, z)

v0, v1 = 6.0, TWO_PI  # narrow band near v-seam
u0, u1 = 0.0, 0.5     # narrow u slice so geometry is non-degenerate

A3 = torus_pt(u0, v0)
B3 = torus_pt(u1, v0)
C3 = torus_pt(u1, v1)
D3 = torus_pt(u0, v1)

p_A = f.cartesian_point(A3)
p_B = f.cartesian_point(B3)
p_C = f.cartesian_point(C3)
p_D = f.cartesian_point(D3)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom v=v0: u from u0→u1
du = u1 - u0
dv = v1 - v0
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], B3[2]-A3[2]), du,
                  (u0, v0), (1.0, 0.0), du)
# Right u=u1: v from v0→v1
e1 = mk_edge_line(v_B, v_C,
                  B3, (C3[0]-B3[0], C3[1]-B3[1], C3[2]-B3[2]), dv,
                  (u1, v0), (0.0, 1.0), dv)
# Top v=v1 (near v-seam): u from u1→u0
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], D3[2]-C3[2]), du,
                  (u1, v1), (-1.0, 0.0), du)
# Left u=u0 (u-iso line near v-seam): v from v1→v0 — THIS IS THE MECHANISM
e3 = mk_edge_line(v_D, v_A,
                  D3, (A3[0]-D3[0], A3[1]-D3[1], A3[2]-D3[2]), dv,
                  (u0, v1), (0.0, -1.0), dv)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE IS the face_geometry;
# u-iso edge near v-seam IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
