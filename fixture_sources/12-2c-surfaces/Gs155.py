"""Gs155 — CopyTrimmedSurface uv-param loss on TOROIDAL_SURFACE.

Catalog claim: ShapeUpgrade_ShapeCopyTool::CopyTrimmedSurface() copies a
RECTANGULAR_TRIMMED_SURFACE wrapping a TOROIDAL_SURFACE but drops the trim
parametrization bounds in the copy. The copied surface's trim range becomes
semantically invalid (reverts to full [0,2π] in both U and V, or undefined),
breaking the face-to-surface pcurve topology that was encoded against the
original restricted bounds.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (major 4.0, minor 1.5) wrapped in RECTANGULAR_TRIMMED_SURFACE
    (u:[0,pi] v:[0,pi]) IS the ADVANCED_FACE.face_geometry; face boundary edge
    pcurves encoded at the trim boundary coordinates IS the mechanism wired into
    face topology; CopyTrimmedSurface losing parametrization bounds in copy IS
    the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE wrapped in RECTANGULAR_TRIMMED_SURFACE
    (u:[0,pi] v:[0,pi]) IS ADVANCED_FACE.face_geometry; face boundary edge
    pcurves at restricted trim-boundary coordinates IS the mechanism wired into
    face topology; CopyTrimmedSurface dropping trim bounds in copy IS the defect.
  - shape_null driver: copy loses trim bounds; pcurve-surface mapping invalid;
    strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs155",
    defect=(
        "TOROIDAL_SURFACE (major 4.0, minor 1.5) wrapped in "
        "RECTANGULAR_TRIMMED_SURFACE (u:[0,pi] v:[0,pi]) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves at restricted "
        "trim-boundary coordinates IS the mechanism wired into face topology; "
        "CopyTrimmedSurface losing parametrization bounds in copy IS the defect; "
        "shape_null"
    ),
)

# ── TOROIDAL_SURFACE: major 4.0, minor 1.5 ─────────────────────────────────────
# Periodic in U and V (full torus). Wrapped in RTS to restrict to
# u:[0,pi] v:[0,pi] — the bounds CopyTrimmedSurface loses in copy.
# Byte assertion: contains(b'RECTANGULAR_TRIMMED_SURFACE')
PI = math.pi
MAJOR = 4.0
MINOR = 1.5

tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs155_tor_ax',#{tor_orig.eid},#{tor_zdir.eid},#{tor_xdir.eid})"
)
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs155_torus',#{tor_ax.eid},{MAJOR},{MINOR})")

# RECTANGULAR_TRIMMED_SURFACE: u:[0,pi] v:[0,pi]
# These are the bounds CopyTrimmedSurface drops in the copy.
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs155_rts',#{torus.eid},0.,{PI:.10f},0.,{PI:.10f},.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: pcurves at restricted trim coordinates ─────────────────────
# TOROIDAL_SURFACE: x = (R + r*cos(v))*cos(u), y = (R + r*cos(v))*sin(u), z = r*sin(v)
# R=4.0, r=1.5. Face corners in 3D at (u,v) corners of the trim rectangle.
def tor_pt(u, v):
    return (
        (MAJOR + MINOR * math.cos(v)) * math.cos(u),
        (MAJOR + MINOR * math.cos(v)) * math.sin(u),
        MINOR * math.sin(v),
    )

A3 = tor_pt(0.0, 0.0)     # (5.5, 0, 0)
B3 = tor_pt(PI,  0.0)     # (-5.5, 0, 0)
C3 = tor_pt(PI,  PI)      # (-2.5, 0, 0) — (R-r)*cos(pi)
D3 = tor_pt(0.0, PI)      # (2.5, 0, 0)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{rts.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom: A→B, u=0→pi at v=0 (restrict v=0 boundary of RTS)
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], B3[2]-A3[2]),
                  abs(B3[0]-A3[0]) + abs(B3[1]-A3[1]),
                  (0.0, 0.0), (1.0, 0.0), PI)
# Right: B→C, v=0→pi at u=pi (restrict u=pi boundary of RTS)
e1 = mk_edge_line(v_B, v_C,
                  B3, (C3[0]-B3[0], C3[1]-B3[1], C3[2]-B3[2]),
                  MINOR * PI,
                  (PI, 0.0), (0.0, 1.0), PI)
# Top: C→D, u=pi→0 at v=pi (restrict v=pi boundary of RTS)
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], D3[2]-C3[2]),
                  abs(D3[0]-C3[0]) + abs(D3[1]-C3[1]),
                  (PI, PI), (-1.0, 0.0), PI)
# Left: D→A, v=pi→0 at u=0 (restrict u=0 boundary of RTS)
e3 = mk_edge_line(v_D, v_A,
                  D3, (A3[0]-D3[0], A3[1]-D3[1], A3[2]-D3[2]),
                  MINOR * PI,
                  (0.0, PI), (0.0, -1.0), PI)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RTS (wrapping TOROIDAL_SURFACE, trim u:[0,pi] v:[0,pi]) IS the face_geometry;
# face boundary edge pcurves at restricted trim-boundary coordinates IS the
# mechanism wired into face topology — exercises CopyTrimmedSurface uv-param
# loss bug.
face  = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
