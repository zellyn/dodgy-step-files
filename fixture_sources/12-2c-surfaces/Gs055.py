"""Gs055 — Composite curve segment with infinite trim parameters.

Catalog claim: A COMPOSITE_CURVE_SEGMENT trims its parent_curve at infinite
(or near-infinite, e.g. 1.0E40) PARAMETER_VALUE literals.  Downstream meshers
cannot evaluate an unbounded trim; translators historically marked such wires
myInfiniteSegment and unwrapped them to a compound of bounded edges.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - A TRIMMED_CURVE with trim parameters PARAMETER_VALUE(-1.0E40) and
    PARAMETER_VALUE(1.0E40) is the parent_curve of a
    COMPOSITE_CURVE_SEGMENT; unbounded trim IS the defect.
  - The COMPOSITE_CURVE IS the curve_3d of the defect EDGE_CURVE's
    SURFACE_CURVE, wiring the infinite-trim segment into face topology.
  - Byte assertions: contains(b'PARAMETER_VALUE(-1.0E40)'),
                     contains(b'PARAMETER_VALUE(1.0E40)'),
                     contains(b'COMPOSITE_CURVE_SEGMENT(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; defect
    TRIMMED_CURVE with trim1=PARAMETER_VALUE(-1.0E40) and
    trim2=PARAMETER_VALUE(1.0E40) IS the parent_curve of the
    COMPOSITE_CURVE_SEGMENT; COMPOSITE_CURVE IS the curve_3d of the defect
    EDGE_CURVE; infinite trim IS wired into face topology.
  - shape_null driver: unbounded trim cannot be evaluated by meshers; strict
    reject kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs055",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "TRIMMED_CURVE(trim1=PARAMETER_VALUE(-1.0E40), trim2=PARAMETER_VALUE(1.0E40)) "
        "IS parent_curve of COMPOSITE_CURVE_SEGMENT; "
        "COMPOSITE_CURVE IS curve_3d of defect EDGE_CURVE; "
        "infinite trim parameters IS wired into face topology; shape_null (strict reject)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs055_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs055_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── TRIMMED_CURVE with infinite PARAMETER_VALUE literals (the defect) ─────────
# Basis curve: a LINE along X
basis_orig = f.cartesian_point((0.0, 0.0, 0.0))
basis_dir  = f.direction((1.0, 0.0, 0.0))
basis_vec  = f.vector(basis_dir, 1.0)
basis_line = f.line(basis_orig, basis_vec)

# Byte assertion: contains(b'PARAMETER_VALUE(-1.0E40)')
# Byte assertion: contains(b'PARAMETER_VALUE(1.0E40)')
# TRIMMED_CURVE(name, basis_curve, trim1, trim2, sense_agreement, master_representation)
# trim1 and trim2 are sets; PARAMETER_VALUE(-1.0E40) and PARAMETER_VALUE(1.0E40) are used.
p_neg_inf = f._emit_raw("PARAMETER_VALUE(-1.0E40)")
p_pos_inf = f._emit_raw("PARAMETER_VALUE(1.0E40)")

trimmed = f._emit_raw(
    f"TRIMMED_CURVE('gs055_tc',#{basis_line.eid},"
    f"(#{p_neg_inf.eid}),(#{p_pos_inf.eid}),.T.,.PARAMETER.)"
)

# ── COMPOSITE_CURVE_SEGMENT referencing the infinite-trim TRIMMED_CURVE ───────
# Byte assertion: contains(b'COMPOSITE_CURVE_SEGMENT(')
ccs_inf = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{trimmed.eid})"
)

# Add a valid second segment for structural completeness
seg2_orig = f.cartesian_point((5.0, 0.0, 0.0))
seg2_dir  = f.direction((0.0, 1.0, 0.0))
seg2_vec  = f.vector(seg2_dir, 4.0)
seg2_line = f.line(seg2_orig, seg2_vec)
ccs_valid = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg2_line.eid})"
)

# COMPOSITE_CURVE containing the infinite-trim segment
comp_curve = f._emit_raw(
    f"COMPOSITE_CURVE('gs055_cc',(#{ccs_inf.eid},#{ccs_valid.eid}),.F.)"
)

# ── Face boundary: defect edge uses COMPOSITE_CURVE as curve_3d ───────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((5.0, 0.0, 0.0))
p_C = f.cartesian_point((5.0, 4.0, 0.0))
p_D = f.cartesian_point((0.0, 4.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: curve_3d IS the COMPOSITE_CURVE (with infinite-trim segment)
p2_e0  = f.cartesian_point((0.0, 0.0))
d2_e0  = f.direction((1.0, 0.0))
v2_e0  = f.vector(d2_e0, 5.0)
l2_e0  = f.line(p2_e0, v2_e0)
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

# PLANE IS the face_geometry; COMPOSITE_CURVE(infinite-trim segment) IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
