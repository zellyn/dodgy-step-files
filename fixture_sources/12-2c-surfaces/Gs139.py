"""Gs139 — IsUClosed pole-singularity false positive.

Catalog claim: ShapeAnalysis_Surface.IsUClosed() validates U-periodicity via
first/last pole comparison but skips validation when poles span conical
singularities. Endpoint poles at apex dominate evaluation, masking parametric
non-closure. Surface reports closure incorrectly.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE IS the ADVANCED_FACE.face_geometry; face boundary spans
    the full 2pi U-range with apex singularity at v=0 causing pole-coincidence
    at the apex that masks non-closure IS the mechanism wired into face topology;
    IsUClosed pole-singularity validation skip IS the defect.
  - Byte assertions: contains(b'CONICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    full-2pi-U face boundary with apex singularity pole-coincidence at v=0
    masking non-closure IS the mechanism wired into face topology;
    IsUClosed missing singularity guard IS the defect.
  - shape_null driver: false U-closure report corrupts seam placement;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs139",
    defect=(
        "CONICAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "full-2pi-U boundary with apex singularity pole-coincidence at v=0 "
        "masking parametric non-closure IS the mechanism wired into face topology; "
        "IsUClosed pole-singularity validation skip IS the defect; shape_null"
    ),
)

# ── CONICAL_SURFACE ────────────────────────────────────────────────────────────
# Byte assertion: contains(b'CONICAL_SURFACE')
# Half-angle = pi/4 (45 deg); at v=0 this is the apex (pole singularity).
# All u-values map to the same 3D apex point at v=0.
# IsUClosed checks first/last pole, sees coincidence (apex), and incorrectly
# reports U-closure even though the surface has parametric non-closure issues.
HALF_ANGLE = math.pi / 4.0
TWO_PI = 2.0 * math.pi

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs139_cone_ax',#{cone_orig.eid},#{cone_zdir.eid},#{cone_xdir.eid})"
)
# CONICAL_SURFACE(name, axis, semi_angle, radius_at_position)
cone = f._emit_raw(f"CONICAL_SURFACE('gs139_cone',#{cone_ax.eid},0.0,{HALF_ANGLE:.10f})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: full 2pi U sweep from near-apex singularity ────────────────
# CONICAL_SURFACE: x = v*cos(u), y = v*sin(u), z = v (half-angle 45 deg)
# At v=0: apex (singularity) — all u values converge to (0,0,0).
# Face strip: v in [0.001, 1.0] (near-apex but not exactly at apex)
# Full U: u in [0, 2pi]
# The apex pole causes first/last-pole coincidence in IsUClosed check.
v_bot, v_top = 0.001, 1.0

def cone_pt(u, v):
    # half-angle 45 deg: x = v*cos(u), y = v*sin(u), z = v
    return (v * math.cos(u), v * math.sin(u), v)

A3 = cone_pt(0.0, v_bot)
B3 = cone_pt(TWO_PI, v_bot)
C3 = cone_pt(TWO_PI, v_top)
D3 = cone_pt(0.0, v_top)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

dv = v_top - v_bot

# Bottom: u=0 → u=2pi at v=v_bot (near-apex ring — small radius)
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], 0.0), TWO_PI * v_bot,
                  (0.0, v_bot), (1.0, 0.0), TWO_PI)
# Right seam: v_bot → v_top at u=2pi
e1 = mk_edge_line(v_B, v_C,
                  B3, (C3[0]-B3[0], C3[1]-B3[1], C3[2]-B3[2]), dv * math.sqrt(2.0),
                  (TWO_PI, v_bot), (0.0, 1.0), dv)
# Top: u=2pi → u=0 at v=v_top
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], 0.0), TWO_PI * v_top,
                  (TWO_PI, v_top), (-1.0, 0.0), TWO_PI)
# Left seam: v_top → v_bot at u=0
e3 = mk_edge_line(v_D, v_A,
                  D3, (A3[0]-D3[0], A3[1]-D3[1], A3[2]-D3[2]), dv * math.sqrt(2.0),
                  (0.0, v_top), (0.0, -1.0), dv)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CONICAL_SURFACE IS the face_geometry;
# full-2pi face boundary near apex singularity IS the mechanism wired into
# face topology (triggers IsUClosed pole-singularity false positive).
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
