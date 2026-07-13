"""Gp176 — COMPOSITE_CURVE segment list out of connected geometric order.

Work packet D1, item `stp-compcurve-reorder` (GAP): "A COMPOSITE_CURVE whose
segment list is out of connected geometric order (segment 2 given before
segment 1, endpoints still connect once reordered) -- must exercise
StepToTopoDS_TranslateCompositeCurve::Init's FixReorder, not an EDGE_LOOP-
level scramble." Mirror: Twi007 covers the *wrong* path (EDGE_LOOP-level
scrambling of 4 independent edges); this fixture instead scrambles the
segment list INSIDE a single COMPOSITE_CURVE that is itself the 3D curve of
ONE EDGE_CURVE.

Modeled directly on Gp034's proven COMPOSITE_CURVE construction (a face on a
PLANE whose bottom edge's 3D curve is a COMPOSITE_CURVE of two LINE
segments), but instead of Gp034's positional GAP between segments, here the
two segments connect EXACTLY (no gap at all -- segment A ends at (5,0,0),
segment B starts at (5,0,0)) and are simply listed in the WRONG order:
COMPOSITE_CURVE('',(seg_B, seg_A),.F.) instead of (seg_A, seg_B). Once
reordered by connectivity, the two segments trace a single continuous path
from A=(0,0,0) to C=(10,0,0) via the midpoint (5,0,0) -- exactly the bottom
edge of the rectangle. The composite curve's own segment list is the sole
defect; the rest of the wire (right/top/left edges) is healthy.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp176",
    defect=(
        "COMPOSITE_CURVE bottom-edge 3D curve lists its two LINE segments "
        "out of connected order: segment[0]=(5,0,0)->(10,0,0) (should be "
        "second) precedes segment[1]=(0,0,0)->(5,0,0) (should be first). "
        "Endpoints connect exactly (no gap, unlike Gp034) once reordered by "
        "connectivity -- exercises composite-curve-level FixReorder, not an "
        "EDGE_LOOP-level scramble (cf. Twi007)."
    ),
)

# Flat PLANE at Z=0 as the host surface.
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane = f.plane(p_axis)

# UV parametric context.
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle corners: A=(0,0,0) B=(10,0,0) C=(10,5,0) D=(0,5,0)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

# ============================================================
# THE DEFECT: COMPOSITE_CURVE for the bottom edge A->B, segments
# listed out of connected order (seg_second before seg_first).
# ============================================================
p_mid = f.cartesian_point((5.0, 0.0, 0.0))

# seg_first (should come first): A -> mid.
d_first = f.direction((1.0, 0.0, 0.0))
v_first = f.vector(d_first, 5.0)
line_first = f.line(p_a, v_first)

# seg_second (should come second): mid -> B.
d_second = f.direction((1.0, 0.0, 0.0))
v_second = f.vector(d_second, 5.0)
line_second = f.line(p_mid, v_second)

seg_first = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{line_first.eid})")
seg_second = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{line_second.eid})")

# Segment list is REORDERED: seg_second listed before seg_first. The two
# segments still connect exactly (mid==mid), just in the wrong list order.
composite_curve = f._emit_raw(
    f"COMPOSITE_CURVE('reordered_composite',(#{seg_second.eid},#{seg_first.eid}),.F.)"
)

# Pcurve for the bottom edge: straight LINE from (0,0) to (10,0) in UV (correct).
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir = f.direction((1.0, 0.0))
pc_bot_vec = f.vector(pc_bot_dir, 10.0)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{plane.eid},#{pc_bot_def.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom_composite',#{composite_curve.eid},"
    f"(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bottom_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Right edge: B -> C (healthy) ----
d_bc = f.direction((0.0, 1.0, 0.0))
v_bc = f.vector(d_bc, 5.0)
line_bc = f.line(p_b, v_bc)
pc_right_start = f.cartesian_point((10.0, 0.0))
pc_right_dir = f.direction((0.0, 1.0))
pc_right_vec = f.vector(pc_right_dir, 5.0)
pc_right_line = f.line(pc_right_start, pc_right_vec)
pc_right_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_pc',#{plane.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_edge',#{line_bc.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_edge',#{v_b.eid},#{v_c.eid},#{sc_right.eid},.T.)"
)

# ---- Top edge: D -> C, traversed reversed C -> D in the loop (healthy) ----
d_dc = f.direction((1.0, 0.0, 0.0))
v_dc = f.vector(d_dc, 10.0)
line_dc = f.line(p_d, v_dc)
pc_top_start = f.cartesian_point((0.0, 5.0))
pc_top_dir = f.direction((1.0, 0.0))
pc_top_vec = f.vector(pc_top_dir, 10.0)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pc',#{plane.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_edge',#{line_dc.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_edge',#{v_d.eid},#{v_c.eid},#{sc_top.eid},.T.)"
)

# ---- Left edge: D -> A (healthy) ----
d_da = f.direction((0.0, -1.0, 0.0))
v_da = f.vector(d_da, 5.0)
line_da = f.line(p_d, v_da)
pc_left_start = f.cartesian_point((0.0, 5.0))
pc_left_dir = f.direction((0.0, -1.0))
pc_left_vec = f.vector(pc_left_dir, 5.0)
pc_left_line = f.line(pc_left_start, pc_left_vec)
pc_left_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left',(#{pc_left_line.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(f"PCURVE('left_pc',#{plane.eid},#{pc_left_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_edge',#{line_da.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_edge',#{v_d.eid},#{v_a.eid},#{sc_left.eid},.T.)"
)

# Loop: bot(fwd A->B, DEFECT) -> right(fwd B->C) -> top(rev C->D) -> left(fwd D->A)
loop = f.edge_loop([
    f.oriented_edge(edge_bot, True),
    f.oriented_edge(edge_right, True),
    f.oriented_edge(edge_top, False),
    f.oriented_edge(edge_left, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
