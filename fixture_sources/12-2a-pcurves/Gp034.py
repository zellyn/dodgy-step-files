"""Gp034 — Composite curve segments do not meet within connectivity tolerance.

Catalog claim (ShapeExtend_ComplexCurve::CheckConnectivity): A COMPOSITE_CURVE
lists multiple segments that are intended to form a single continuous curve.
Segment N's last 3D point sits at a distance of several millimetres from segment
N+1's first 3D point; far beyond any reasonable connectivity tolerance. The
composite curve is not actually connected; treating it as one curve produces
invalid downstream geometry.

Catalog recipe: Two LINE-based EDGE_CURVEs whose vertices are at (5,0,0) and
(5.005,0,0) respectively. Both edges share a wire but the kernel must report a
5e-3 disconnect. The byte assertion requires EDGE_CURVE.

Fixture: A face on a PLANE. The face has two edges whose shared "vertex" in 3D
is actually two distinct CARTESIAN_POINTs: segment1 ends at (5,0,0) and
segment2 starts at (5.005,0,0) — a 5mm gap. Both edges are wrapped as
EDGE_CURVEs, and their junction vertices are two distinct VERTEX_POINTs even
though one oriented_edge's end-vertex nominally matches the next's start-vertex
in the topological wire.

To make this a proper COMPOSITE_CURVE defect (not just a bad wire), the two
edges' 3D LINE curves are referenced as COMPOSITE_CURVE_SEGMENT entries in a
COMPOSITE_CURVE. A second EDGE_CURVE uses this composite curve as its geometry.
The composite curve's internal gap of 5mm is the defect.

The face topology is a rectangle on the Z=0 plane: 4 edges, proper 4-vertex loop.
The bottom edge uses the defective composite curve.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp034",
    defect=(
        "COMPOSITE_CURVE of two LINE segments: segment-1 ends at (5.0,0,0) but "
        "segment-2 starts at (5.005,0,0), a 5mm gap far beyond connectivity "
        "tolerance; kernel must report gap or refuse; OCC silently accepts"
    ),
)

# Flat PLANE at Z=0 as the host surface.
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref  = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane  = f.plane(p_axis)

# UV parametric context (the plane's own XY is UV).
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle corners in the plane (Z=0):
#   A = (0, 0, 0), B = (10, 0, 0), C = (10, 5, 0), D = (0, 5, 0)
p_a = f.cartesian_point((0.0,  0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 5.0, 0.0))
p_d = f.cartesian_point(( 0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

# ============================================================
# THE DEFECT: COMPOSITE_CURVE for the bottom edge A->B.
#
# Segment-1: A=(0,0,0) -> gap_end=(5.0,0,0)
# Segment-2: gap_start=(5.005,0,0) -> B=(10,0,0)
# Gap = 5mm between (5.0,0,0) and (5.005,0,0).
# ============================================================

# Segment-1 end point and segment-2 start point (gap pair):
p_gap_end   = f.cartesian_point((5.0,   0.0, 0.0))
p_gap_start = f.cartesian_point((5.005, 0.0, 0.0))

# 3D LINE for segment 1: from A to gap_end.
d_seg1 = f.direction((1.0, 0.0, 0.0))
v_seg1 = f.vector(d_seg1, 5.0)  # length 5.0
line_seg1 = f.line(p_a, v_seg1)

# 3D LINE for segment 2: from gap_start to B.
d_seg2 = f.direction((1.0, 0.0, 0.0))
v_seg2 = f.vector(d_seg2, 4.995)  # 10.0 - 5.005 = 4.995
line_seg2 = f.line(p_gap_start, v_seg2)

# COMPOSITE_CURVE_SEGMENTs wrapping the two lines.
# COMPOSITE_CURVE_SEGMENT(transition_code, same_sense, parent_curve)
seg1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{line_seg1.eid})"
)
seg2 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{line_seg2.eid})"
)

# COMPOSITE_CURVE: lists both segments. The gap between seg1 end and seg2 start
# is the defect.
composite_curve = f._emit_raw(
    f"COMPOSITE_CURVE('gapped_composite',(#{seg1.eid},#{seg2.eid}),.F.)"
)

# Pcurve for the bottom edge on the plane: LINE from (0,0) to (10,0) in UV.
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 10.0)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{plane.eid},#{pc_bot_def.eid})")

# SURFACE_CURVE for bottom edge: 3D = composite_curve (with gap), pcurve = correct.
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom_composite',#{composite_curve.eid},"
    f"(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bottom_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Right edge: B -> C (straight vertical line) ----
p_bc_dir = f.direction((0.0, 1.0, 0.0))
v_bc     = f.vector(p_bc_dir, 5.0)
line_bc  = f.line(p_b, v_bc)
pc_right_start = f.cartesian_point((10.0, 0.0))
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 5.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
pc_right_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_pc',#{plane.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_edge',#{line_bc.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_edge',#{v_b.eid},#{v_c.eid},#{sc_right.eid},.T.)"
)

# ---- Top edge: C -> D (reversed, so D -> C traversed backward) ----
p_dc_dir = f.direction((1.0, 0.0, 0.0))
v_dc     = f.vector(p_dc_dir, 10.0)
line_dc  = f.line(p_d, v_dc)
pc_top_start = f.cartesian_point((0.0, 5.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, 10.0)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pc',#{plane.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_edge',#{line_dc.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_edge',#{v_d.eid},#{v_c.eid},#{sc_top.eid},.T.)"
)

# ---- Left edge: D -> A (vertical line going down) ----
p_da_dir = f.direction((0.0, -1.0, 0.0))
v_da     = f.vector(p_da_dir, 5.0)
line_da  = f.line(p_d, v_da)
pc_left_start = f.cartesian_point((0.0, 5.0))
pc_left_dir   = f.direction((0.0, -1.0))
pc_left_vec   = f.vector(pc_left_dir, 5.0)
pc_left_line  = f.line(pc_left_start, pc_left_vec)
pc_left_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left',(#{pc_left_line.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(f"PCURVE('left_pc',#{plane.eid},#{pc_left_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_edge',#{line_da.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_edge',#{v_d.eid},#{v_a.eid},#{sc_left.eid},.T.)"
)

# Loop: bot(fwd A->B) -> right(fwd B->C) -> top(rev C->D, i.e. D->C reversed)
#       -> left(fwd D->A)
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),   # A->B (composite curve with gap)
    f.oriented_edge(edge_right, True),   # B->C
    f.oriented_edge(edge_top,   False),  # C->D (reversed: edge goes D->C)
    f.oriented_edge(edge_left,  True),   # D->A
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
