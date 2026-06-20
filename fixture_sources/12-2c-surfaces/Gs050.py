"""Gs050 — Toroidal surface stored incorrectly: major / minor swapped.

Catalog claim: TOROIDAL_SURFACE('',#axis, 0.5, 5.0) where the intended
torus has major_radius=5.0 and minor_radius=0.5.  Producer emitted the
values reversed.  Reader interprets literally → minor > major → apple/lemon
geometry (no central hole).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE with swapped radii (0.5, 5.0) IS the
    ADVANCED_FACE.face_geometry; reversed proportions IS the defect wired
    into face topology.
  - Byte assertions: contains(b'TOROIDAL_SURFACE('),
                     contains(b'0.5,5.0').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE (major_radius=0.5, minor_radius=5.0 —
    values swapped; minor ≥ major creates apple/lemon, not a valid torus) IS
    the ADVANCED_FACE.face_geometry; swapped-radius TOROIDAL_SURFACE IS
    wired into face topology.
  - shape_null driver: minor ≥ major is geometrically degenerate (no central
    hole); strict reject kernels flag and produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs050",
    defect=(
        "TOROIDAL_SURFACE('',#axis,0.5,5.0) with major_radius=0.5, minor_radius=5.0 "
        "(values swapped; minor > major → apple/lemon, degenerate torus) IS "
        "ADVANCED_FACE.face_geometry; swapped-radius TOROIDAL_SURFACE IS wired "
        "into face topology; shape_null (strict reject)"
    ),
)

# ── CATALOG MECHANISM: TOROIDAL_SURFACE with swapped radii (the defect) ──────
# Byte assertion: contains(b'TOROIDAL_SURFACE(')
# Byte assertion: contains(b'0.5,5.0')
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs050_tor_ax',#{tor_orig.eid},#{tor_zdir.eid},#{tor_xdir.eid})"
)
# major=0.5, minor=5.0 — swapped; intended major=5.0, minor=0.5
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs050_torus',#{tor_ax.eid},0.5,5.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the defect TOROIDAL_SURFACE ─────────────────────
# Use a simple rectangular patch in torus parameter space: U ∈ [0,2π], V ∈ [0,2π]
# Corner 3D points: sample at (U,V) = (0,0), (π/2,0), (π/2,π/2), (0,π/2)
# For minor=5, major=0.5 the 3D evaluation is unusual; use representative coords.
p_A = f.cartesian_point(( 5.5,  0.0, 0.0))
p_B = f.cartesian_point(( 0.0,  5.5, 0.0))
p_C = f.cartesian_point((-5.5,  0.0, 0.0))
p_D = f.cartesian_point(( 0.0, -5.5, 0.0))

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

import math
e0 = mk_edge_line(v_A, v_B, ( 5.5, 0.0, 0.0), (-1.0, 1.0, 0.0), 5.5*math.sqrt(2),
                  (0.0, 0.0), (1.0, 0.0), math.pi/2)
e1 = mk_edge_line(v_B, v_C, ( 0.0, 5.5, 0.0), (-1.0,-1.0, 0.0), 5.5*math.sqrt(2),
                  (math.pi/2, 0.0), (1.0, 0.0), math.pi/2)
e2 = mk_edge_line(v_C, v_D, (-5.5, 0.0, 0.0), ( 1.0,-1.0, 0.0), 5.5*math.sqrt(2),
                  (math.pi, 0.0), (1.0, 0.0), math.pi/2)
e3 = mk_edge_line(v_D, v_A, ( 0.0,-5.5, 0.0), ( 1.0, 1.0, 0.0), 5.5*math.sqrt(2),
                  (3*math.pi/2, 0.0), (1.0, 0.0), math.pi/2)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE (swapped radii) IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
