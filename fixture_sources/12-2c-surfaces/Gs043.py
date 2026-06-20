"""Gs043 — OFFSET_CURVE_3D with ref_distance equal to basis curve radius of curvature.

Catalog claim: CIRCLE radius 5.0; OFFSET_CURVE_3D over it with
ref_distance = -5.0 → entire curve collapses to center point. The
mathematical offset is undefined at every point (offset point coincides with
the center of curvature; 0/0 in first derivative). Strict kernels must detect
collapse / cusp at construction time and reject or treat as point set.

OCC behavior: silently accepts (empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - OFFSET_CURVE_3D over a CIRCLE radius 5.0 with ref_distance=-5.0 IS the
    defect: entire offset collapses to the center; IS the curve_3d of the
    defect EDGE_CURVE's SURFACE_CURVE.
  - Byte assertions: contains(b'OFFSET_CURVE_3D('),
                     contains(b'-5.0'),
                     contains(b'CIRCLE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry;
    OFFSET_CURVE_3D with ref_distance=-5.0 over CIRCLE(radius=5.0) —
    collapse to center — IS curve_3d of defect EDGE_CURVE; degenerate
    offset IS wired into face topology.
  - shape_null driver: collapsed offset curve undefined; strict
    heal-or-reject kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs043",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "OFFSET_CURVE_3D over CIRCLE(radius=5.0) with ref_distance=-5.0 "
        "(entire offset collapses to center) IS curve_3d of defect EDGE_CURVE; "
        "collapsed offset IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
ax3   = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs043_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs043_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── BASIS CURVE: CIRCLE radius 5.0 ────────────────────────────────────────────
# Byte assertion: contains(b'CIRCLE(')
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs043_circ_ax',#{circ_orig.eid},#{circ_zdir.eid},#{circ_xdir.eid})"
)
circle = f._emit_raw(f"CIRCLE('gs043_circle',#{circ_ax.eid},5.0)")

# ── OFFSET_CURVE_3D: ref_distance = -5.0 (collapses to center) ───────────────
# OFFSET_CURVE_3D(name, basis_curve, ref_distance, self_intersect, ref_direction)
# ref_distance=-5.0 == -radius → full collapse; 0/0 in derivative everywhere.
# Byte assertion: contains(b'OFFSET_CURVE_3D(')
# Byte assertion: contains(b'-5.0')
offset_dir = f.direction((0.0, 0.0, 1.0))  # offset normal direction
oc3d = f._emit_raw(
    f"OFFSET_CURVE_3D('gs043_oc3d',#{circle.eid},-5.0,.F.,#{offset_dir.eid})"
)

# ── Face boundary: defect edge E0 uses OFFSET_CURVE_3D as curve_3d ───────────
p_A = f.cartesian_point((5.0, 0.0, 0.0))
p_B = f.cartesian_point((0.0, 5.0, 0.0))
p_C = f.cartesian_point((-5.0, 0.0, 0.0))
p_D = f.cartesian_point((0.0, -5.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: curve_3d IS the OFFSET_CURVE_3D (collapsed circle)
p2_e0 = f.cartesian_point((1.0, 0.0))
d2_e0 = f.direction((0.0, 1.0))
v2_e0 = f.vector(d2_e0, 1.0)
l2_e0 = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{plane.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{oc3d.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

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
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_edge_line(v_B, v_C, (0.0,5.0,0.0), (-1.0,0.0,0.0), 5.0, (0.0,1.0), (-1.0,0.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (-5.0,0.0,0.0), (0.0,-1.0,0.0), 5.0, (-1.0,0.0), (0.0,-1.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (0.0,-5.0,0.0), (1.0,0.0,0.0), 5.0, (0.0,-1.0), (1.0,0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; OFFSET_CURVE_3D(collapsed) IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
