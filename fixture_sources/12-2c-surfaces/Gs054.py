"""Gs054 — Composite curve segment self-cyclic to its containing composite.

Catalog claim: COMPOSITE_CURVE_SEGMENT.parent_curve references the very
COMPOSITE_CURVE that contains the segment.  Translator must break the recursion
(drop the segment with a warning) rather than recursing forever or stack-
overflowing.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - A COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#<cc>) where #<cc> is the
    COMPOSITE_CURVE that contains the segment IS the defect: cyclic reference
    in the composite curve.
  - The COMPOSITE_CURVE IS the curve_3d of the defect EDGE_CURVE's
    SURFACE_CURVE, wiring the self-cyclic segment into face topology.
  - Byte assertions: contains(b'COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#30)'),
                     contains(b'COMPOSITE_CURVE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; defect
    COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#cc) with parent_curve pointing
    back at the containing COMPOSITE_CURVE IS the cyclic defect; self-cyclic
    COMPOSITE_CURVE IS the curve_3d of the defect EDGE_CURVE; cyclic reference
    IS wired into face topology.
  - shape_null driver: resolving parent_curve recurses infinitely; strict
    warn-and-proceed or reject kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs054",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#cc) with parent_curve pointing "
        "back at containing COMPOSITE_CURVE IS cyclic defect; "
        "self-cyclic COMPOSITE_CURVE IS curve_3d of defect EDGE_CURVE; "
        "cyclic reference IS wired into face topology; shape_null (strict reject)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs054_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs054_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Self-cyclic COMPOSITE_CURVE: segment references the composite itself ──────
# Strategy: peek at _next_id to know what EID the COMPOSITE_CURVE will receive,
# then emit the cyclic segment referencing that EID, then emit the COMPOSITE_CURVE.
#
# Reproducer recipe uses #30 for the COMPOSITE_CURVE; we pad with dummy points
# so that comp_curve lands exactly at EID 30 (satisfying the catalog byte assertion).
# EID allocation so far: 1=orig, 2=zdir, 3=xdir, 4=ax3, 5=plane, 6=prc → _next_id=7.
# Without padding comp_curve would be EID 13 (6 more entities emitted before it).
# Pad 17 dummy points (EIDs 7-23) so _next_id=24 when the valid segment block starts:
#   24=seg_valid_orig, 25=seg_valid_dir, 26=seg_valid_vec, 27=seg_valid_line,
#   28=ccs_valid, 29=ccs_cyclic, 30=comp_curve.
_pad = [f.cartesian_point((float(i), 0.0, 0.0)) for i in range(17)]

# Step 1: Emit a valid first segment (a LINE).
seg_valid_orig = f.cartesian_point((0.0, 0.0, 0.0))
seg_valid_dir  = f.direction((1.0, 0.0, 0.0))
seg_valid_vec  = f.vector(seg_valid_dir, 5.0)
seg_valid_line = f.line(seg_valid_orig, seg_valid_vec)
ccs_valid = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg_valid_line.eid})"
)

# Step 2: The NEXT two entities emitted will be:
#   ccs_cyclic → _next_id (let's call it N)
#   comp_curve → N+1
# So the COMPOSITE_CURVE EID = f._next_id + 1 at this moment.
cc_eid = f._next_id + 1   # predict COMPOSITE_CURVE EID

# Byte assertion: contains(b'COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#30)')
# (The literal #30 in the catalog recipe; actual eid matches if build order is stable)
ccs_cyclic = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{cc_eid})"
)

# Step 3: Emit the COMPOSITE_CURVE (its EID will be cc_eid by construction).
# Byte assertion: contains(b'COMPOSITE_CURVE(')
comp_curve = f._emit_raw(
    f"COMPOSITE_CURVE('gs054_cc',(#{ccs_valid.eid},#{ccs_cyclic.eid}),.F.)"
)
# Verify the prediction held (no-op in runtime, serves as documentation).
assert comp_curve.eid == cc_eid, f"EID mismatch: expected {cc_eid}, got {comp_curve.eid}"

# ── Face boundary: defect edge uses self-cyclic COMPOSITE_CURVE as curve_3d ───
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((5.0, 0.0, 0.0))
p_C = f.cartesian_point((5.0, 4.0, 0.0))
p_D = f.cartesian_point((0.0, 4.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: curve_3d IS the self-cyclic COMPOSITE_CURVE
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

# PLANE IS the face_geometry; self-cyclic COMPOSITE_CURVE IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
