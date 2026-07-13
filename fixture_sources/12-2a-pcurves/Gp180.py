"""Gp180 — 2D pcurve knot vector with a near-zero-length span after Bezier
decomposition (2D-curve sibling of Gn042's surface-side case).

Work packet D1, item `tkshh-near-zero-knot-span-thin-patch-filter`
(PARTIAL, missing 1 of 2): "A 2D pcurve (B-spline) whose knot vector has a
near-duplicate/clustered knot pair producing a near-zero-length arc after
Bezier decomposition (Gn042 is the surface-side sibling -- mirror onto a 2D
curve)." problem_id `tkshh-near-zero-knot-span-thin-patch-filter`
(ShapeUpgrade_ConvertCurve2dToBezier::Compute() near-zero knot-interval
filter, ShapeUpgrade_ConvertCurve2dToBezier.cxx:188-209): during Bezier
decomposition, an interior knot whose multiplicity is one short of the
curve's degree gets raised to full multiplicity by inserting one more copy
of the SAME knot value -- creating a knot interval of literally zero width
at that parameter. The filter is supposed to detect and drop the resulting
zero-length Bezier arc rather than emit it into the decomposed segment set.

Geometry: reuses Gn042's exact numeric pattern (degree 3, 6 control points,
knots (0.0, 0.5, 1.0), multiplicities (4, 2, 4) -- interior knot 0.5 sits
at multiplicity 2, one short of the degree-3 full-multiplicity value of 3)
but applies it to a 2D PCURVE instead of a B_SPLINE_SURFACE. The pcurve's
6 control points are evenly spaced and exactly collinear along (0,0) ->
(10,0), so the curve traces the same straight segment as its host edge's
3D LINE regardless of the pathological knot vector -- isolating the defect
to the knot structure alone, with nothing else (3D curve, host PLANE,
other edges) malformed.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp180",
    defect=(
        "Bottom edge's 2D PCURVE (degree 3, 6 collinear control points "
        "along (0,0)->(10,0)) uses Gn042's exact knot pattern -- knots "
        "(0.0,0.5,1.0), multiplicities (4,2,4) -- so the interior knot at "
        "0.5 sits one multiplicity short of full (degree=3); Bezier "
        "decomposition (ShapeUpgrade_ConvertCurve2dToBezier) must insert "
        "one more copy of 0.5, producing a zero-width knot interval "
        "[0.5,0.5] the thin-patch filter should drop. The 3D curve is a "
        "plain, healthy LINE -- the defect is isolated to the pcurve knots."
    ),
)

# Flat PLANE at Z=0 as the host surface.
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane = f.plane(p_axis)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle corners (Z=0): A=(0,0,0) B=(10,0,0) C=(10,5,0) D=(0,5,0)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

# ---- Bottom edge A->B: THE DEFECT is in the pcurve knot vector only. ----
d_ab = f.direction((1.0, 0.0, 0.0))
v_ab = f.vector(d_ab, 10.0)
line_ab = f.line(p_a, v_ab)  # healthy 3D curve

# 2D pcurve: degree 3, 6 collinear control points along (0,0)->(10,0),
# knots (0.0,0.5,1.0), multiplicities (4,2,4) -- Gn042's pattern.
pc0 = f.cartesian_point((0.0, 0.0))
pc1 = f.cartesian_point((2.0, 0.0))
pc2 = f.cartesian_point((4.0, 0.0))
pc3 = f.cartesian_point((6.0, 0.0))
pc4 = f.cartesian_point((8.0, 0.0))
pc5 = f.cartesian_point((10.0, 0.0))
pcurve2d_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('near_zero_knot_span_pc',3,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid},#{pc3.eid},#{pc4.eid},#{pc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(4,2,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_def',(#{pcurve2d_bspline.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc_thin_patch',#{plane.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom_edge_sc',#{line_ab.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bottom_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Right edge B->C (healthy) ----
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

# ---- Top edge D->C, traversed reversed (healthy) ----
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

# ---- Left edge D->A (healthy) ----
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
