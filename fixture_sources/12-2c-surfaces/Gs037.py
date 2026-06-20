"""Gs037 — Offset of a surface-of-linear-extrusion fails iso-curve evaluation.

Catalog claim: A face's supporting surface is an OFFSET_SURFACE over a
SURFACE_OF_LINEAR_EXTRUSION. Evaluating an iso-curve (row of constant U or V)
throws because the iso-evaluation logic does not descend through the
offset/extrusion wrappers to the basis curve.

OCC behavior: silently accepts (empty result). live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - OFFSET_SURFACE over SURFACE_OF_LINEAR_EXTRUSION IS the ADVANCED_FACE.face_geometry.
  - The OFFSET_SURFACE wraps the SURFACE_OF_LINEAR_EXTRUSION with offset distance 2.0.
  - A rectangular wire with PCURVE/SURFACE_CURVE edges is wired onto the composite
    surface, triggering the iso-curve evaluation path.
  - Byte assertions: contains(b'OFFSET_SURFACE('),
                     contains(b'SURFACE_OF_LINEAR_EXTRUSION(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE IS the ADVANCED_FACE.face_geometry;
    OFFSET_SURFACE wraps SURFACE_OF_LINEAR_EXTRUSION; composite surface chain
    IS wired into face topology; iso-curve evaluation cannot descend through
    composite surface wrappers.
  - shape_null driver: iso-curve evaluation failure on OFFSET_SURFACE→SOLE chain;
    strict heal-or-reject kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs037",
    defect=(
        "OFFSET_SURFACE over SURFACE_OF_LINEAR_EXTRUSION IS ADVANCED_FACE.face_geometry; "
        "composite surface chain OFFSET_SURFACE→SURFACE_OF_LINEAR_EXTRUSION IS wired into "
        "face topology; iso-curve evaluation cannot descend through offset wrappers; shape(1) (live OCC heals)"
    ),
)

# ── BASIS CURVE for SURFACE_OF_LINEAR_EXTRUSION ───────────────────────────────
# A line in the XZ plane (not parallel to extrusion direction Y, so not degenerate).
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 0.0, 0.0))   # X direction
line_vec  = f.vector(line_dir, 10.0)
basis_line = f.line(line_orig, line_vec)

# Extrusion direction: Y axis (perpendicular to line direction X — valid, non-degenerate).
ext_dir = f.direction((0.0, 1.0, 0.0))
ext_vec = f.vector(ext_dir, 8.0)

# SURFACE_OF_LINEAR_EXTRUSION: extrude X-line in Y direction → XY plane strip
# Byte assertion: contains(b'SURFACE_OF_LINEAR_EXTRUSION(')
sole = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('gs037_sole',#{basis_line.eid},#{ext_vec.eid})"
)

# OFFSET_SURFACE wrapping the SURFACE_OF_LINEAR_EXTRUSION, offset distance=2.0
# OFFSET_SURFACE(name, basis_surface, distance, self_intersect)
# Byte assertion: contains(b'OFFSET_SURFACE(')
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('gs037_offset',#{sole.eid},2.0,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the OFFSET_SURFACE ───────────────────────────────
# Parametric space of SOLE: u along X (0..10), v along Y (0..8).
# Offset shifts normals by 2 in Z; 3D corners approx at z=2 (offset).
p_A = f.cartesian_point((0.0, 0.0, 2.0))
p_B = f.cartesian_point((5.0, 0.0, 2.0))
p_C = f.cartesian_point((5.0, 4.0, 2.0))
p_D = f.cartesian_point((0.0, 4.0, 2.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{offset_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,2.0), (1.0,0.0,0.0), 5.0, (0.0,0.0), (1.0,0.0), 5.0)
e1 = mk_edge_line(v_B, v_C, (5.0,0.0,2.0), (0.0,1.0,0.0), 4.0, (5.0,0.0), (0.0,1.0), 4.0)
e2 = mk_edge_line(v_C, v_D, (5.0,4.0,2.0), (-1.0,0.0,0.0), 5.0, (5.0,4.0), (-1.0,0.0), 5.0)
e3 = mk_edge_line(v_D, v_A, (0.0,4.0,2.0), (0.0,-1.0,0.0), 4.0, (0.0,4.0), (0.0,-1.0), 4.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# OFFSET_SURFACE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], offset_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
