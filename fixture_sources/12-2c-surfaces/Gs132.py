"""Gs132 — TOROIDAL_SURFACE wrongly elevated to non-analytic Bezier.

Catalog claim: ShapeUpgrade_SplitSurfaceContinuity.Compute is called on an
analytic surface (C-infinity continuous, like TOROIDAL_SURFACE). The method
attempts to split and elevate continuity via Bezier approximation, producing
a non-analytic BSpline surface with wrong continuity class.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE IS the ADVANCED_FACE.face_geometry; face boundary spans
    a full 2pi U-range with a seam edge that forces SplitSurfaceContinuity
    to process the analytic surface IS the mechanism wired into face topology;
    SplitSurfaceContinuity.Compute incorrect Bezier elevation of analytic
    surface IS the defect.
  - Byte assertions: contains(b'TOROIDAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry;
    full-2pi-U seam edge triggers SplitSurfaceContinuity.Compute on the
    analytic surface IS the mechanism wired into face topology;
    Bezier elevation of C-inf analytic surface to wrong continuity class
    IS the defect.
  - shape_null driver: non-analytic approximation has wrong continuity
    class; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs132",
    defect=(
        "TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "full-2pi-U seam edge forcing SplitSurfaceContinuity.Compute on "
        "analytic surface IS the mechanism wired into face topology; "
        "Bezier elevation of C-inf analytic surface to wrong continuity class "
        "IS the defect; shape_null"
    ),
)

# ── TOROIDAL_SURFACE ───────────────────────────────────────────────────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
# Major radius R=1, minor radius r=0.3
# Full U-range [0, 2pi]: seam forces SplitSurfaceContinuity to process
# the analytic torus surface — mechanism that triggers the defect.
R, r = 1.0, 0.3
TWO_PI = 2.0 * math.pi

torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_zdir = f.direction((0.0, 0.0, 1.0))
torus_xdir = f.direction((1.0, 0.0, 0.0))
torus_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs132_torus_ax',#{torus_orig.eid},#{torus_zdir.eid},#{torus_xdir.eid})"
)
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs132_torus',#{torus_ax.eid},1.0,0.3)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: full 2pi U-strip with explicit seam ────────────────────────
# The seam at u=0=2pi is what forces SplitSurfaceContinuity to attempt
# Bezier elevation on this analytic TOROIDAL_SURFACE.
# V-strip: v in [0, pi/2]
v0, v1 = 0.0, math.pi / 2.0

def torus_pt(u, v):
    x = (R + r * math.cos(v)) * math.cos(u)
    y = (R + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    return (x, y, z)

# Seam vertices: u=0 and u=2pi map to same 3D point (seam coincidence)
A3 = torus_pt(0.0, v0)   # u=0,   v=v0
B3 = torus_pt(TWO_PI, v0)  # u=2pi, v=v0 (same 3D as A3)
C3 = torus_pt(TWO_PI, v1)  # u=2pi, v=v1
D3 = torus_pt(0.0, v1)   # u=0,   v=v1

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

# Bottom: u=0 → u=2pi at v=v0 (full U sweep)
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], B3[2]-A3[2]), TWO_PI * (R + r),
                  (0.0, v0), (1.0, 0.0), TWO_PI)
# Right seam: v0 → v1 at u=2pi
e1 = mk_edge_line(v_B, v_C,
                  B3, (C3[0]-B3[0], C3[1]-B3[1], C3[2]-B3[2]), dv,
                  (TWO_PI, v0), (0.0, 1.0), dv)
# Top: u=2pi → u=0 at v=v1
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], D3[2]-C3[2]), TWO_PI * (R + r * math.cos(v1)),
                  (TWO_PI, v1), (-1.0, 0.0), TWO_PI)
# Left seam: v1 → v0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  D3, (A3[0]-D3[0], A3[1]-D3[1], A3[2]-D3[2]), dv,
                  (0.0, v1), (0.0, -1.0), dv)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE IS the face_geometry;
# full-2pi seam edge IS the mechanism wired into face topology.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
