"""Gp184 — 3D B-spline curve with a genuine C0 interior knot, reachable in a
live translated face (curve subvariant of seq-split-continuity, missing 1
of 3 -- the pcurve and surface subvariants already survive via Gp120/
Gs049/Gs070; the curve subvariant's only prior witness, Gp033, is
occt=empty).

Work packet D2, item `seq-split-continuity` (PARTIAL, missing 1 of 3),
problem_id `seq-split-continuity`: "Curves ... whose internal smoothness
is below the required continuity class ... must be divided at the
discontinuity points" (ShapeUpgrade_ShapeDivideContinuity, static
splitcontinuity, ShapeProcess_OperLibrary.cxx:438-475).

Deviation from the packet spec, evidence-based: the spec text (mirroring
Gp033's own recipe) asks for "multiplicity = degree+1" at the interior
knot. Empirically tested against this repo's live OCP/OCCT 7.8.1: a
degree-2 B_SPLINE_CURVE_WITH_KNOTS with interior knot multiplicity 3 (=
degree+1) is REJECTED outright by Geom_BSplineCurve's constructor
("BSpline curve: # Poles and degree mismatch" -- OCCT enforces interior
knot multiplicity <= degree; only the first/last knot of a clamped curve
may reach degree+1). That is exactly why Gp033 is shape_null: the curve
entity itself never constructs, so translation fails before the edge is
even reachable. To be genuinely LIVE (the packet's actual ask), this
fixture instead uses interior multiplicity = degree (2), which OCCT's
constructor accepts and which IS the textbook C0 case: position-
continuous, tangent-discontinuous. Non-collinear neighbour control
points on either side of the shared knot-point ensure the kink is a real
geometric tangent break, not an accidental smooth pass-through.

Mechanism: A face on a PLANE. The bottom edge's 3D curve is a degree-2
B_SPLINE_CURVE_WITH_KNOTS, 5 control points, knot vector (0,0,0,0.5,1,1,1)
i.e. multiplicities (3,1,3) -- wait, C0 at an interior knot for a degree-2
curve needs multiplicity 2 there, not 1. Correct knot vector: (0,0,0, 0.5,
0.5, 1,1,1), multiplicities (3,2,3), 5 control points (5 = sum(mults) -
degree - 1 = 8-3). Pole 2 (index 2, the interior knot's own control
point) is SHARED by both sides (so position is continuous), but poles 1
and 3 are placed so the incoming and outgoing tangent directions at pole
2 genuinely differ (non-collinear). The edge is wired through EDGE_CURVE
-> PCURVE -> SURFACE_CURVE -> ADVANCED_FACE like every other edge in this
fixture; the whole 4-edge loop is a normal rectangle so translation
reaches a live shape(1), not Gp033's shape_null or Gn172's orphan
pattern.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp184",
    defect=(
        "Bottom edge 3D curve: degree-2 B_SPLINE_CURVE_WITH_KNOTS, 5 control "
        "points, knot vector (0,0,0,0.5,0.5,1,1,1) i.e. multiplicities (3,2,3) -- "
        "interior multiplicity = degree (2) gives genuine C0 continuity (position "
        "continuous, tangent discontinuous); poles either side of the shared knot "
        "point are non-collinear so the kink is geometrically real; wired through "
        "a live EDGE_CURVE/PCURVE into a reachable ADVANCED_FACE (not Gp033's "
        "unconstructible mult=degree+1 interior knot, which OCCT's Geom_"
        "BSplineCurve constructor rejects outright, yielding shape_null)"
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

# Rectangle corners: A=(0,0,0), B=(10,0,0), C=(10,5,0), D=(0,5,0).
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

# ---- THE DEFECT: bottom edge A->B, degree-2 B-spline with a genuine C0
# interior knot at u=0.5 (multiplicity = degree = 2). 5 control points;
# pole index 2 sits exactly on the line A->B (so 3D endpoints A, B stay
# correct and the curve stays position-continuous through the knot), but
# poles 1 and 3 are offset to opposite sides (z-bump up then down) so the
# incoming tangent (pole1->pole2) and outgoing tangent (pole2->pole3)
# genuinely differ in direction -- a real geometric kink, not an
# accidentally-smooth pass-through.
# NOTE: an earlier symmetric choice here (bump +Z before the knot, bump
# -Z after, both offset equally from the straight A-B line) was tested
# live and turned out to be an ACCIDENTAL C1 pass-through: for that
# point-symmetric arrangement, direction(c2-c1) == direction(c3-c2)
# exactly, so BRepAdaptor_Curve.D1() straddling the knot reported
# IDENTICAL tangents on both sides -- no real kink despite the double
# interior knot. Fixed by bumping in DIFFERENT axes on each side (Y
# before the knot, Z after), which live-verified as a genuine tangent
# discontinuity: direction(c2-c1) = (2.5,-0.6,0), direction(c3-c2) =
# (2.5,0,0.6) -- not parallel.
c0 = f.cartesian_point((0.0, 0.0, 0.0))    # = A
c1 = f.cartesian_point((2.5, 0.6, 0.0))    # bump in +Y before the knot
c2 = f.cartesian_point((5.0, 0.0, 0.0))    # ON the A-B line -- shared knot point
c3 = f.cartesian_point((7.5, 0.0, 0.6))    # bump in +Z after the knot
c4 = f.cartesian_point((10.0, 0.0, 0.0))   # = B

bot_bspline = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[c0, c1, c2, c3, c4],
    knot_multiplicities=[3, 2, 3],
    knots=[0.0, 0.5, 1.0],
    name="c0_kink_bottom",
)
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir = f.direction((1.0, 0.0))
pc_bot_vec = f.vector(pc_bot_dir, 10.0)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{plane.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('c0_bot',#{bot_bspline.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('c0_bot',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Right edge: B -> C (straight vertical line) ----
v_bc = f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)
line_bc = f.line(p_b, v_bc)
pc_right_start = f.cartesian_point((10.0, 0.0))
pc_right_vec = f.vector(f.direction((0.0, 1.0)), 5.0)
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

# ---- Top edge: D -> C (used reversed in the loop) ----
v_dc = f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)
line_dc = f.line(p_d, v_dc)
pc_top_start = f.cartesian_point((0.0, 5.0))
pc_top_vec = f.vector(f.direction((1.0, 0.0)), 10.0)
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

# ---- Left edge: D -> A (vertical line going down) ----
v_da = f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)
line_da = f.line(p_d, v_da)
pc_left_start = f.cartesian_point((0.0, 5.0))
pc_left_vec = f.vector(f.direction((0.0, -1.0)), 5.0)
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

# Loop: bot(fwd A->B, C0 kink) -> right(fwd B->C) -> top(rev C->D) -> left(fwd D->A)
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
