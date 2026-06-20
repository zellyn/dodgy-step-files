"""Gs035 — Composite curve segment with null parent_curve.

Catalog claim: COMPOSITE_CURVE_SEGMENT.parent_curve is null ($). Translator
must drop the null segment with a warning rather than dereferencing $ as a curve.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - A COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,$) with null parent_curve IS
    the defect: it is referenced by a COMPOSITE_CURVE.
  - The COMPOSITE_CURVE IS the curve_3d of the defect EDGE_CURVE's SURFACE_CURVE,
    wiring the null-parent-curve segment into face topology.
  - Byte assertions: contains(b'COMPOSITE_CURVE_SEGMENT('),
                     contains(b',$)'),
                     contains(b'COMPOSITE_CURVE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; the defect
    COMPOSITE_CURVE_SEGMENT with parent_curve=$ IS a segment of the COMPOSITE_CURVE
    that IS the curve_3d of the defect EDGE_CURVE; null reference IS wired into
    face topology.
  - shape_null driver: dereferencing $ crashes; strict warn-and-proceed or reject
    kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs035",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,$) with parent_curve=$ IS segment "
        "of COMPOSITE_CURVE which IS curve_3d of defect EDGE_CURVE; "
        "null parent_curve reference IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs035_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs035_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── COMPOSITE_CURVE with a null-parent_curve segment (the defect) ─────────────
# Segment 1: a valid LINE segment for the composite curve.
seg1_orig = f.cartesian_point((0.0, 0.0, 0.0))
seg1_dir  = f.direction((1.0, 0.0, 0.0))
seg1_vec  = f.vector(seg1_dir, 5.0)
seg1_line = f.line(seg1_orig, seg1_vec)

ccs1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg1_line.eid})"
)

# Segment 2: DEFECT — parent_curve IS null ($).
# Byte assertions: contains(b'COMPOSITE_CURVE_SEGMENT('), contains(b',$)')
ccs2 = f._emit_raw(
    "COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,$)"
)

# COMPOSITE_CURVE referencing both segments — byte assertion: contains(b'COMPOSITE_CURVE(')
comp_curve = f._emit_raw(
    f"COMPOSITE_CURVE('gs035_cc',(#{ccs1.eid},#{ccs2.eid}),.F.)"
)

# ── Face boundary: defect edge E0 uses COMPOSITE_CURVE as curve_3d ───────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((5.0, 0.0, 0.0))
p_C = f.cartesian_point((5.0, 4.0, 0.0))
p_D = f.cartesian_point((0.0, 4.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: curve_3d IS the COMPOSITE_CURVE (with null segment)
p2_e0 = f.cartesian_point((0.0, 0.0))
d2_e0 = f.direction((1.0, 0.0))
v2_e0 = f.vector(d2_e0, 5.0)
l2_e0 = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{plane.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(
    f"SURFACE_CURVE('sc_e0',#{comp_curve.eid},(#{pc_e0.eid}),.PCURVE_S1.)"
)
e0 = f._emit_raw(
    f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)"
)

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

e1 = mk_edge_line(v_B, v_C, (5.0,0.0,0.0), (0.0,1.0,0.0), 4.0, (5.0,0.0), (0.0,1.0), 4.0)
e2 = mk_edge_line(v_C, v_D, (5.0,4.0,0.0), (-1.0,0.0,0.0), 5.0, (5.0,4.0), (-1.0,0.0), 5.0)
e3 = mk_edge_line(v_D, v_A, (0.0,4.0,0.0), (0.0,-1.0,0.0), 4.0, (0.0,4.0), (0.0,-1.0), 4.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; COMPOSITE_CURVE(null segment) IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
