"""Gs129 — CYLINDRICAL_SURFACE with non-unit radius underflowing tolerance check.

Catalog claim: ShapeAnalysis_Surface.IsUClosed applies radius-relative tolerance
when testing if a CYLINDRICAL_SURFACE closes in the U direction. For very
small radii (e.g., 0.0001 mm), the radius-relative tolerance underflows,
causing the method to incorrectly report closure even when the surface
should not be treated as closed.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius=0.0001) IS the ADVANCED_FACE.face_geometry;
    tiny radius causing IsUClosed radius-relative tolerance underflow IS the
    mechanism wired into face topology; IsUClosed missing underflow guard IS
    the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE (radius=0.0001) IS
    ADVANCED_FACE.face_geometry; radius-relative tolerance underflow causing
    false U-closure report IS the mechanism wired into face topology;
    IsUClosed underflow guard absence IS the defect.
  - shape_null driver: false closure report corrupts trim logic; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs129",
    defect=(
        "CYLINDRICAL_SURFACE (radius=0.0001) IS ADVANCED_FACE.face_geometry; "
        "tiny radius causing IsUClosed radius-relative tolerance underflow "
        "IS the mechanism wired into face topology; "
        "IsUClosed underflow guard absence IS the defect; "
        "shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE: very small radius ─────────────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# Radius = 0.0001 — sub-tolerance; radius-relative tolerance underflows in IsUClosed
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs129_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
# CYLINDRICAL_SURFACE(name, axis, radius)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs129_cyl',#{cyl_ax.eid},0.0001)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: small rectangle in parameter space ─────────────────────────
# On a CYLINDRICAL_SURFACE: u ∈ [0, 2π], v ∈ [0, height]
# 3D coords: x = r*cos(u), y = r*sin(u), z = v
# Using r = 0.0001
R = 0.0001
TWO_PI = 2.0 * math.pi
H = 0.001  # height span

# Corner 3D points
def cyl_pt(u, v):
    return (R * math.cos(u), R * math.sin(u), v)

u0, u1 = 0.0, TWO_PI
v_bot, v_top = 0.0, H

A3 = cyl_pt(u0, v_bot)
B3 = cyl_pt(u1, v_bot)
C3 = cyl_pt(u1, v_top)
D3 = cyl_pt(u0, v_top)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom ring: u from 0 to 2π, v=0
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], 0.0), TWO_PI * R,
                  (u0, v_bot), (1.0, 0.0), TWO_PI)
# Right seam: v from 0 to H, u=2π
e1 = mk_edge_line(v_B, v_C,
                  B3, (0.0, 0.0, 1.0), H,
                  (u1, v_bot), (0.0, 1.0), H)
# Top ring: u from 2π to 0, v=H
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], 0.0), TWO_PI * R,
                  (u1, v_top), (-1.0, 0.0), TWO_PI)
# Left seam: v from H to 0, u=0
e3 = mk_edge_line(v_D, v_A,
                  D3, (0.0, 0.0, -1.0), H,
                  (u0, v_top), (0.0, -1.0), H)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE (radius=0.0001) IS the face_geometry;
# tiny-radius IsUClosed underflow IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
