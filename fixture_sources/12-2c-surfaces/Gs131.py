"""Gs131 — TOROIDAL_SURFACE with Newton iteration near convergence.

Catalog claim: ShapeAnalysis_Surface.NextValueOfUV implements Newton iteration
to find UV coordinates on a surface for a given 3D point. When the
previous iterate is very close to the target (within Confusion tolerance),
the algorithm declares convergence prematurely without verifying that the
residual 3D distance is actually below tolerance.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE IS the ADVANCED_FACE.face_geometry; face edge 3D curve
    lies at a 3D point that maps to a UV location within Confusion tolerance
    of the seam but on the wrong side, causing premature Newton convergence
    IS the mechanism wired into face topology; NextValueOfUV missing
    residual-verification IS the defect.
  - Byte assertions: contains(b'TOROIDAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry;
    face edge 3D curve placed at 3D point within Confusion tolerance of
    parameter seam IS the mechanism wired into face topology;
    NextValueOfUV premature convergence without residual check IS the defect.
  - shape_null driver: wrong UV returned → trim references wrong surface
    region; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs131",
    defect=(
        "TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "face edge 3D curve placed within Confusion tolerance of u=2π seam "
        "causing premature Newton convergence to wrong UV "
        "IS the mechanism wired into face topology; "
        "NextValueOfUV residual-verification absence IS the defect; "
        "shape_null"
    ),
)

# ── TOROIDAL_SURFACE ───────────────────────────────────────────────────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
# Major radius R=1, minor radius r=0.3
# Torus axis along Z; u-seam at u=0=2π
R, r = 1.0, 0.3
TWO_PI = 2.0 * math.pi

torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_zdir = f.direction((0.0, 0.0, 1.0))
torus_xdir = f.direction((1.0, 0.0, 0.0))
torus_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs131_torus_ax',#{torus_orig.eid},#{torus_zdir.eid},#{torus_xdir.eid})"
)
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs131_torus',#{torus_ax.eid},1.0,0.3)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: strip straddling the u-seam within Confusion tolerance ──────
# Confusion tolerance in OCCT is typically 1e-7.
# We place the strip so that its left edge is at u = 2π - 1e-8 (just before seam)
# and right edge at u = 2π + 1e-8 (just after seam wraps to u=0+1e-8).
# Newton iteration starting from u=0 side converges prematurely to the seam
# point instead of crossing correctly.
EPS = 1e-8  # within Confusion tolerance (1e-7 in OCCT)
u0 = TWO_PI - EPS   # just before seam
u1 = EPS            # just after seam (= TWO_PI + EPS wrapped)
v0, v1 = 0.0, 0.5  # moderate v span

def torus_pt(u, v):
    x = (R + r * math.cos(v)) * math.cos(u)
    y = (R + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    return (x, y, z)

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

dv = v1 - v0

# Bottom: u0→u1 at v=v0 (crosses seam within Confusion tolerance)
# The 3D displacement is tiny (EPS*2 around the torus) — mechanism
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], B3[2]-A3[2]), 2*EPS,
                  (u0, v0), (1.0, 0.0), 2*EPS)
# Right: v0→v1 at u=u1
e1 = mk_edge_line(v_B, v_C,
                  B3, (C3[0]-B3[0], C3[1]-B3[1], C3[2]-B3[2]), dv,
                  (u1, v0), (0.0, 1.0), dv)
# Top: u1→u0 at v=v1
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], D3[2]-C3[2]), 2*EPS,
                  (u1, v1), (-1.0, 0.0), 2*EPS)
# Left: v1→v0 at u=u0 (just before seam — premature-convergence edge)
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
# face edges straddling seam within Confusion tolerance IS the mechanism
# wired into face topology (triggers premature Newton convergence).
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
