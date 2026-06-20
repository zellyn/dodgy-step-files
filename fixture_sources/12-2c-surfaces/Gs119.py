"""Gs119 — CONICAL_SURFACE with zero radius (degenerate point).

Catalog claim: CONICAL_SURFACE with radius=0 and arbitrary semi-angle
collapses to a degenerate point at the apex. ShapeAnalysis_Surface.IsDegenerated
fails to detect this because its radius test uses `radius > 0` (strict greater-than)
without applying abs(), so a zero-radius cone is not flagged.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE (radius=0.0, semi_angle=0.785398) IS the
    ADVANCED_FACE.face_geometry; zero-radius cone degenerate at apex IS
    the mechanism wired into face topology; IsDegenerated() `radius > 0`
    strict test (without abs) misses zero radius IS the defect.
  - Byte assertions: contains(b'CONICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE (radius=0.0) IS the ADVANCED_FACE.face_geometry;
    zero-radius degenerate cone collapsing to apex point IS the mechanism wired
    into face topology; IsDegenerated() strict `radius > 0` without abs() fails
    to detect zero radius IS the defect.
  - shape_null driver: degenerate point-cone; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs119",
    defect=(
        "CONICAL_SURFACE (radius=0.0, semi_angle=pi/4) IS ADVANCED_FACE.face_geometry; "
        "zero-radius cone degenerate at apex IS the mechanism wired into face topology; "
        "IsDegenerated() strict radius>0 without abs() fails to detect zero radius "
        "IS the defect; shape_null"
    ),
)

# ── CONICAL_SURFACE: zero radius, non-zero semi-angle ─────────────────────────
# Byte assertion: contains(b'CONICAL_SURFACE')
# A cone with radius=0 collapses to its apex — degenerate point surface.
# Semi-angle = pi/4 (45 degrees) is well-defined but irrelevant when radius=0.
cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs119_cone_ax',#{cone_orig.eid},#{cone_zdir.eid},#{cone_xdir.eid})"
)
# CONICAL_SURFACE(name, position, radius, semi_angle)
semi_angle = math.pi / 4.0   # 45 degrees
cone = f._emit_raw(
    f"CONICAL_SURFACE('gs119_cone',#{cone_ax.eid},0.0,{semi_angle:.6f})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit patch in (u,v) parameter space ───────────────────────
# For a cone: 3D point = (radius + v*sin(half_angle))*cos(u),
#                         (radius + v*sin(half_angle))*sin(u), v*cos(half_angle))
# With radius=0: 3D = (v*sin(pi/4)*cos(u), v*sin(pi/4)*sin(u), v*cos(pi/4))
# At v=0 (apex), all u values map to (0,0,0) → degenerate edge.
# Boundary: u in [0, 2*pi], v in [0, 1].
# Simplified to a unit-square-like param patch; 3D edges approximate cone geometry.
# Bottom edge (v=0): entire edge collapses to apex (0,0,0) — degenerate.
# Top edge (v=1): circle at height cos(pi/4) with radius sin(pi/4).
p_apex   = f.cartesian_point((0.0, 0.0, 0.0))      # v=0 apex (all u)
p_top0   = f.cartesian_point((math.sin(math.pi/4), 0.0, math.cos(math.pi/4)))   # u=0,v=1
p_top1   = f.cartesian_point((math.sin(math.pi/4), 0.0, math.cos(math.pi/4)))   # u=2pi,v=1 (same)

v_apex0  = f.vertex_point(p_apex)
v_apex1  = f.vertex_point(p_apex)   # second vertex at apex (loop closure)
v_top0   = f.vertex_point(p_top0)
v_top1   = f.vertex_point(p_top1)

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

# Use rectangular param domain u∈[0,1] (scaled from 0 to 2π), v∈[0,1].
# e0: bottom seam apex at u=0 to v=1 (left edge, u=0)
e0 = mk_edge_line(v_apex0, v_top0,
                  (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.001,
                  (0.0, 0.0), (0.0, 1.0), 1.0)
# e1: top rim u: 0→1 (v=1, 3D circle at height)
r_top = math.sin(math.pi / 4)
e1 = mk_edge_line(v_top0, v_top1,
                  (r_top, 0.0, math.cos(math.pi/4)), (0.0, 1.0, 0.0), 0.001,
                  (0.0, 1.0), (1.0, 0.0), 1.0)
# e2: right edge v=1→0 at u=1 (back to apex)
e2 = mk_edge_line(v_top1, v_apex1,
                  (r_top, 0.0, math.cos(math.pi/4)), (0.0, 0.0, -1.0), 0.001,
                  (1.0, 1.0), (0.0, -1.0), 1.0)
# e3: bottom seam v=0 at u=1→0 (degenerate: all at apex)
e3 = mk_edge_line(v_apex1, v_apex0,
                  (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 0.001,
                  (1.0, 0.0), (-1.0, 0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CONICAL_SURFACE (radius=0) IS the face_geometry;
# zero-radius degenerate apex IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
