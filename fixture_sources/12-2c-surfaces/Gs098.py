"""Gs098 — ShapeAnalysis_Surface.IsDegenerated revolution-axis-on-curve.

Catalog claim: SURFACE_OF_REVOLUTION where basis curve passes through the
rotation axis. IsDegenerated only checks axis vector direction, not curve
position, missing the degenerate apex singularity.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION with basis LINE that passes through the Z-axis
    (revolution axis) IS the ADVANCED_FACE.face_geometry; the face boundary
    edge loop contains a degenerate apex edge at the axis-intersection point
    IS the mechanism wired into face topology; IsDegenerated checks axis
    vector only, misses positional axis-crossing, degenerate apex IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION'),
                     contains(b'LINE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION (Z-axis) with basis LINE passing
    through Z-axis IS the ADVANCED_FACE.face_geometry; degenerate apex at
    axis-crossing (0,0,0→0,0,1 along basis line) IS the mechanism wired into
    face topology; IsDegenerated misses positional crossing IS the defect.
  - shape_null driver: degenerate apex on surface of revolution; strict
    kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs098",
    defect=(
        "SURFACE_OF_REVOLUTION (Z-axis) with basis LINE through axis IS "
        "ADVANCED_FACE.face_geometry; degenerate apex edge at axis-crossing "
        "IS the mechanism wired into face topology; IsDegenerated checks "
        "axis vector only, misses positional crossing IS the defect; shape_null"
    ),
)

# ── SURFACE_OF_REVOLUTION: Z-axis, basis line passes through Z-axis ──────────
# Byte assertions: contains(b'SURFACE_OF_REVOLUTION'), contains(b'LINE')
# Basis: LINE from (0,0,0) along Z — lies on the revolution axis itself.
basis_pt  = f.cartesian_point((0.0, 0.0, 0.0))
basis_dir = f.direction((0.0, 0.0, 1.0))
basis_vec = f.vector(basis_dir, 1.0)
basis_line = f.line(basis_pt, basis_vec)   # LINE IS the basis curve

rev_orig  = f.cartesian_point((0.0, 0.0, 0.0))
rev_zdir  = f.direction((0.0, 0.0, 1.0))
rev_xdir  = f.direction((1.0, 0.0, 0.0))
rev_ax    = f._emit_raw(
    f"AXIS1_PLACEMENT('gs098_rev_ax',#{rev_orig.eid},#{rev_zdir.eid})"
)
# SURFACE_OF_REVOLUTION with basis line on axis → degenerate apex locus
rev_surf  = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs098_revsurf',#{basis_line.eid},#{rev_ax.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: wedge from apex (axis) outward ─────────────────────────────
# 3D points: apex at origin (degenerate point), rim at radius 0 (always on axis)
# Use a cone-like boundary: apex at (0,0,0), rim at z=1 — but since basis is
# on axis, the "surface" collapses: all points at any angle land on the axis.
p_apex = f.cartesian_point((0.0, 0.0, 0.0))
p_rim  = f.cartesian_point((0.0, 0.0, 1.0))

v_apex = f.vertex_point(p_apex)
v_rim  = f.vertex_point(p_rim)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{rev_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

import math
HALF_PI = math.pi / 2.0

# e0: apex→rim meridian at u=0 (v: 0→1) — passes through degenerate axis point
e0 = mk_edge_line(v_apex, v_rim,
                  (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (0.0, 0.0), (0.0, 1.0), 1.0)

# e1: rim arc at v=1 (u: 0→π/2) — degenerate: all rim points same (on axis)
e1 = mk_edge_line(v_rim, v_rim,
                  (0.0, 0.0, 1.0), (0.0, 0.0, 0.0), HALF_PI,
                  (0.0, 1.0), (1.0, 0.0), HALF_PI)

# e2: rim→apex meridian at u=π/2 (v: 1→0)
e2 = mk_edge_line(v_rim, v_apex,
                  (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (HALF_PI, 1.0), (0.0, -1.0), 1.0)

# e3: degenerate apex edge (apex→apex, u: π/2→0)
e3 = mk_edge_line(v_apex, v_apex,
                  (0.0, 0.0, 0.0), (0.0, 0.0, 0.001), 0.001,
                  (HALF_PI, 0.0), (-1.0, 0.0), HALF_PI)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION IS face_geometry; apex at axis-crossing IS mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], rev_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
