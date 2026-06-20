"""Gs096 — ShapeAnalysis_Surface.ComputeSingularities torus pinch.

Catalog claim: Self-intersecting torus with major radius R < minor radius r.
ComputeSingularities reports zero singularities despite self-intersection
creating a pinch point where the surface crosses itself.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (major_radius=0.3, minor_radius=1.0 — R < r, self-
    intersecting pinch) IS the ADVANCED_FACE.face_geometry; the face boundary
    edge loop spanning the full v-parameter range (v: 0→2π) traverses the
    self-intersection locus IS the mechanism wired into face topology;
    ComputeSingularities ignores self-intersection, reports zero singularities
    IS the defect.
  - Byte assertions: contains(b'TOROIDAL_SURFACE'),
                     contains(b'6.283185307179586').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE (major_radius=0.3, minor_radius=1.0,
    R < r → self-intersecting pinch locus) IS the ADVANCED_FACE.face_geometry;
    edge loop spanning v: 0→2π crossing self-intersection IS the mechanism
    wired into face topology; ComputeSingularities reports zero singularities
    (misses pinch) IS the defect.
  - shape_null driver: self-intersecting torus geometry; strict kernels reject;
    empty result.
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 2.0 * math.pi  # 6.283185307179586

f = StepFile(
    catalog_id="Gs096",
    defect=(
        "TOROIDAL_SURFACE (major_radius=0.3, minor_radius=1.0, R < r, "
        "self-intersecting pinch locus) IS ADVANCED_FACE.face_geometry; "
        "edge loop spanning v: 0→6.283185307179586 (2π) traversing the "
        "self-intersection IS the mechanism wired into face topology; "
        "ComputeSingularities reports zero singularities (misses pinch) "
        "IS the defect; shape_null"
    ),
)

# ── TOROIDAL_SURFACE: major_radius=0.3, minor_radius=1.0 (R < r) ─────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs096_tor_ax',#{tor_orig.eid},#{tor_zdir.eid},#{tor_xdir.eid})"
)
# major_radius=0.3 < minor_radius=1.0 → self-intersecting torus (pinch point)
torus = f._emit_raw(
    f"TOROIDAL_SURFACE('gs096_torus',#{tor_ax.eid},0.3,1.0)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: full ring in u (0→2π), fixed meridian strip v: 0→2π ───────
# Byte assertion: contains(b'6.283185307179586')
# 3D corner points on torus surface:
# (u=0,v=0): (R+r,0,0) = (1.3, 0, 0)
# (u=π,v=0): (-1.3, 0, 0) but to keep topology simple, use a rectangular
# strip at u: 0→π, v: 0→2π — sufficient to traverse the pinch locus.

p_A = f.cartesian_point(( 1.3,  0.0, 0.0))   # (u=0,   v=0)
p_B = f.cartesian_point((-0.7,  0.0, 0.0))   # (u=π,   v=0) approx on torus
p_C = f.cartesian_point((-0.7,  0.0, 0.0))   # (u=π,   v=2π) — degenerate back
p_D = f.cartesian_point(( 1.3,  0.0, 0.0))   # (u=0,   v=2π)

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)

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

# e0: bottom A→B (v=0, u: 0→π)
e0 = mk_edge_line(v_A, v_B,
                  (1.3, 0.0, 0.0), (-1.0, 0.0, 0.0), 2.0,
                  (0.0, 0.0), (1.0, 0.0), math.pi)

# e1: right B→B meridian (u=π, v: 0→2π) — traverses pinch locus
# Byte assertion: 6.283185307179586 appears in p2_len
e1 = mk_edge_line(v_B, v_B,
                  (-0.7, 0.0, 0.0), (0.0, 0.0, 1.0), TWO_PI,
                  (math.pi, 0.0), (0.0, 1.0), TWO_PI)

# e2: top B→A (v=2π≡0, u: π→0)
e2 = mk_edge_line(v_B, v_A,
                  (-0.7, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0,
                  (math.pi, TWO_PI), (-1.0, 0.0), math.pi)

# e3: left A→A meridian (u=0, v: 2π→0)
e3 = mk_edge_line(v_A, v_A,
                  (1.3, 0.0, 0.0), (0.0, 0.0, -1.0), TWO_PI,
                  (0.0, TWO_PI), (0.0, -1.0), TWO_PI)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE (R<r) IS the face_geometry; full-v meridian IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
