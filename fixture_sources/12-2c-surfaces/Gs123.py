"""Gs123 — TOROIDAL_SURFACE with major_radius < minor_radius (self-intersecting).

Catalog claim: ShapeAnalysis_Surface.IsVClosed reports true for a self-intersecting
torus where major_radius < minor_radius. The geometry is degenerate (torus touches
itself) but IsVClosed doesn't detect the invalid configuration.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (major_radius=0.5, minor_radius=1.0) IS the
    ADVANCED_FACE.face_geometry; major_radius < minor_radius produces a
    self-intersecting torus whose inner equator passes through the axis IS the
    mechanism wired into face topology; IsVClosed accepting self-intersecting
    torus without major/minor radius comparison IS the defect.
  - Byte assertions: contains(b'TOROIDAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE (major_radius=0.5, minor_radius=1.0,
    so minor > major) IS the ADVANCED_FACE.face_geometry; self-intersecting
    spindle torus geometry IS the mechanism wired into face topology;
    IsVClosed not checking major≥minor IS the defect.
  - shape_null driver: self-intersecting torus is geometrically invalid;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs123",
    defect=(
        "TOROIDAL_SURFACE (major_radius=0.5, minor_radius=1.0; minor > major) "
        "IS ADVANCED_FACE.face_geometry; "
        "self-intersecting spindle torus (major_radius < minor_radius) "
        "IS the mechanism wired into face topology; "
        "IsVClosed not comparing major vs minor radius IS the defect; "
        "shape_null"
    ),
)

# ── TOROIDAL_SURFACE: major_radius < minor_radius ─────────────────────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
# major_radius=0.5, minor_radius=1.0 → inner equator at R-r = 0.5-1.0 = -0.5
# (passes through and beyond axis) → self-intersecting spindle torus.
torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_zdir = f.direction((0.0, 0.0, 1.0))
torus_xdir = f.direction((1.0, 0.0, 0.0))
torus_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs123_torus_ax',#{torus_orig.eid},#{torus_zdir.eid},#{torus_xdir.eid})"
)
# TOROIDAL_SURFACE(name, position, major_radius, minor_radius)
torus = f._emit_raw(
    f"TOROIDAL_SURFACE('gs123_torus',#{torus_ax.eid},0.5,1.0)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in (u,v) parameter space ──────────────────────
# For torus: u = longitude [0, 2π), v = latitude [0, 2π).
# Use simplified unit param square; 3D points approximate torus geometry at
# major=0.5, minor=1.0 (self-intersecting).
# At u=0,v=0: x=(R+r*cos(0))*cos(0) = R+r = 1.5, y=0, z=r*sin(0)=0
import math
R, r = 0.5, 1.0
p_A_3d = ((R + r) * math.cos(0), (R + r) * math.sin(0), 0.0)   # u=0, v=0
p_B_3d = ((R + r) * math.cos(0), (R + r) * math.sin(0), 0.0)   # u=1, v=0 (approx same)
p_C_3d = ((R + r) * math.cos(0), (R + r) * math.sin(0), 0.0)   # u=1, v=1 (approx same)
p_D_3d = ((R + r) * math.cos(0), (R + r) * math.sin(0), 0.0)   # u=0, v=1 (approx same)

p_A = f.cartesian_point(p_A_3d)
p_B = f.cartesian_point(p_B_3d)
p_C = f.cartesian_point(p_C_3d)
p_D = f.cartesian_point(p_D_3d)

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

e0 = mk_edge_line(v_A, v_B,
                  p_A_3d, (0.0, 1.0, 0.0), 0.001,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
e1 = mk_edge_line(v_B, v_C,
                  p_B_3d, (0.0, 0.0, 1.0), 0.001,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D,
                  p_C_3d, (0.0, -1.0, 0.0), 0.001,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
e3 = mk_edge_line(v_D, v_A,
                  p_D_3d, (0.0, 0.0, -1.0), 0.001,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE (major_radius=0.5 < minor_radius=1.0) IS the face_geometry;
# self-intersecting spindle torus IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
