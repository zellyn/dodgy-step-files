"""Gs032 — Surface-of-linear-extrusion whose direction is parallel to its basis line.

Catalog claim: A SURFACE_OF_LINEAR_EXTRUSION whose basis curve is a LINE
collinear with the extrusion direction is degenerate; it collapses to a line.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - SURFACE_OF_LINEAR_EXTRUSION IS the ADVANCED_FACE.face_geometry.
  - BASIS CURVE is a LINE with direction (0,0,1); extrusion_axis VECTOR has
    direction (0,0,1) — exactly parallel to the LINE direction.
  - Byte assertions: contains(b'SURFACE_OF_LINEAR_EXTRUSION('),
                     count_entity_def(b'LINE') == 1.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_LINEAR_EXTRUSION IS the
    ADVANCED_FACE.face_geometry; basis LINE direction == extrusion direction
    (both (0,0,1)); collapsed surface IS wired into face topology.
  - shape_null driver: extrusion direction parallel to basis line collapses
    the surface to a line; strict reject-or-warn kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs032",
    defect=(
        "SURFACE_OF_LINEAR_EXTRUSION IS ADVANCED_FACE.face_geometry; "
        "basis LINE direction=(0,0,1) IS parallel to extrusion_axis direction=(0,0,1); "
        "count_entity_def(LINE)==1; surface collapses to line; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: SURFACE_OF_LINEAR_EXTRUSION with basis LINE parallel to extrusion ──
# Byte assertion: count_entity_def(b'LINE') == 1 — this is the ONLY LINE in the file.
# All wire edges must use a non-LINE curve type.
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((0.0, 0.0, 1.0))    # basis LINE runs along Z axis
line_vec  = f.vector(line_dir, 10.0)
basis_line = f.line(line_orig, line_vec)     # THE one and only LINE entity

# Extrusion direction also (0,0,1) — PARALLEL to basis LINE direction — this IS the defect.
ext_dir = f.direction((0.0, 0.0, 1.0))
ext_vec = f.vector(ext_dir, 5.0)

# SURFACE_OF_LINEAR_EXTRUSION(name, swept_curve, extrusion_axis)
surf = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('gs032_sole',#{basis_line.eid},#{ext_vec.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary using B_SPLINE_CURVE_WITH_KNOTS (avoids LINE entities in wire) ──
# Parametric space: u = parameter along basis line (0..1), v = extrusion (0..1).
# Wire corners: degenerate surface collapses all to Z axis, so use trivial 3D pts.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((0.0, 0.0, 5.0))
p_C = f.cartesian_point((0.0, 0.0, 3.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

def mk_bspline_edge(vs, ve, cp3_list, cp2_list):
    """Build a degree-1 B_SPLINE_CURVE edge with matching pcurve on surf."""
    # 3D B-spline control points (degree 1 = polyline)
    cps3 = [f.cartesian_point(c) for c in cp3_list]
    n = len(cps3)
    cp_ids3 = "(" + ",".join(f"#{p.eid}" for p in cps3) + ")"
    mults   = f"(2,{','.join(['1']*(n-2))},2)" if n > 2 else "(2,2)"
    knots   = "(" + ",".join(str(float(i)) for i in range(n)) + ")"
    bsp3 = f._emit_raw(
        f"B_SPLINE_CURVE_WITH_KNOTS('',1,{cp_ids3},.UNSPECIFIED.,.F.,.F.,"
        f"{mults},{knots},.UNSPECIFIED.)"
    )
    # 2D pcurve B-spline control points
    cps2 = [f.cartesian_point(c) for c in cp2_list]
    cp_ids2 = "(" + ",".join(f"#{p.eid}" for p in cps2) + ")"
    bsp2 = f._emit_raw(
        f"B_SPLINE_CURVE_WITH_KNOTS('',1,{cp_ids2},.UNSPECIFIED.,.F.,.F.,"
        f"{mults},{knots},.UNSPECIFIED.)"
    )
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{bsp2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{bsp3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Triangle in 3D and parametric space (no LINEs used — only B_SPLINE_CURVE_WITH_KNOTS)
e0 = mk_bspline_edge(v_A, v_B,
    [(0.0,0.0,0.0), (0.0,0.0,5.0)],
    [(0.0,0.0),     (0.0,1.0)])
e1 = mk_bspline_edge(v_B, v_C,
    [(0.0,0.0,5.0), (0.0,0.0,3.0)],
    [(0.0,1.0),     (0.5,0.5)])
e2 = mk_bspline_edge(v_C, v_A,
    [(0.0,0.0,3.0), (0.0,0.0,0.0)],
    [(0.5,0.5),     (0.0,0.0)])

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])

# SURFACE_OF_LINEAR_EXTRUSION IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
