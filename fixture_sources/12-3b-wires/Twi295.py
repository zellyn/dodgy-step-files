"""Twi295 — Chain of two tangent-continuous cubic Bezier (B-spline) edges
that should be concatenated into one curve under ConcatBSplines mode
(missing subvariant of tkshh-same-curve-fragmented-edges, distinct from
Twi089's collinear-LINE case and Twi294's same-CIRCLE-arc case).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-same-curve-fragmented-edges, subvariant "B-spline/Bezier edge chain
concatenated into one curve (ConcatBSplines mode)" — evidence:
ShapeUpgrade_UnifySameDomain::MergeSubSeq B-spline/Bezier concatenation
when myConcatBSplines, ShapeUpgrade_UnifySameDomain.cxx:2262). Unlike the
LINE case (parallel-direction test) or the CIRCLE case (coincident-centre
test), B-spline/Bezier edges don't have a single analytic "same curve"
predicate — ConcatBSplines mode instead requires the two curves to be
geometrically compatible (same degree here, and G1/tangent-continuous at
the shared vertex) before GeomConvert/BSplCLib concatenates their pole
and knot sequences into a single spliced curve. This fixture's two
EDGE_CURVEs are DISTINCT B_SPLINE_CURVE_WITH_KNOTS entities (degree 3,
4 poles each, no internal knots — i.e. two ordinary cubic Bezier arcs),
positioned so the shared vertex's incoming and outgoing tangent
directions agree exactly ((1,-1,0) on both sides), meeting at a degree-2
vertex not used by any other wire/face.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP (mirrors
Twi089/Twi294's structure): two B_SPLINE_CURVE_WITH_KNOTS-based
EDGE_CURVEs sharing a tangent-continuous degree-2 VERTEX_POINT.
GEOMETRIC_CURVE_SET IS the model entity — OCC returns empty for this
container type (same convention as Twi089/Twi253/Twi294).

Byte assertions:
  - contains(b'bspline_chain_loop')
  - contains(b'mid_bspline_vertex')
  - count_entity_def(b'EDGE_CURVE') == 2
  - count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi295",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'bspline_chain_loop'; exactly "
        "TWO EDGE_CURVEs, each on a DISTINCT degree-3 B_SPLINE_CURVE_WITH_KNOTS "
        "(4 poles, no internal knots -- an ordinary cubic Bezier arc); "
        "e1 poles (0,0,0)-(1,1,0)-(2,1,0)-(3,0,0); e2 poles "
        "(3,0,0)-(4,-1,0)-(5,-1,0)-(6,0,0) -- the incoming tangent direction at "
        "the shared point ((3,0,0)-(2,1,0) == (1,-1,0)) exactly equals the "
        "outgoing tangent direction ((4,-1,0)-(3,0,0) == (1,-1,0)): genuinely "
        "G1/tangent-continuous, a real ConcatBSplines candidate, not just two "
        "unrelated curves that happen to touch; "
        "shared VERTEX_POINT 'mid_bspline_vertex' at (3,0,0) -- degree-2 vertex "
        "not used by any other face; "
        "ShapeUpgrade_UnifySameDomain (myConcatBSplines mode) should splice the "
        "two pole/knot sequences into one concatenated B-spline edge; "
        "GEOMETRIC_CURVE_SET IS the model entity -- OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 1.0, 0.0))
p2 = f.cartesian_point((2.0, 1.0, 0.0))
p3 = f.cartesian_point((3.0, 0.0, 0.0))
p4 = f.cartesian_point((4.0, -1.0, 0.0))
p5 = f.cartesian_point((5.0, -1.0, 0.0))
p6 = f.cartesian_point((6.0, 0.0, 0.0))

v_start = f.vertex_point(p0)
# Byte assertion: contains(b'mid_bspline_vertex') -- degree-2, unused-elsewhere,
# tangent-continuous junction vertex
v_mid = f.vertex_point(p3, name="mid_bspline_vertex")
v_end = f.vertex_point(p6)

# e1: cubic Bezier (degree 3, no internal knots) from p0 to p3
curve1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[p0, p1, p2, p3],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
e1 = f.edge_curve(v_start, v_mid, curve1)
oe1 = f.oriented_edge(e1, True)

# e2: cubic Bezier (degree 3, no internal knots) from p3 to p6, G1-continuous
# with e1 at the shared vertex (identical tangent direction (1,-1,0))
curve2 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[p3, p4, p5, p6],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
e2 = f.edge_curve(v_mid, v_end, curve2)
oe2 = f.oriented_edge(e2, True)

# EDGE_LOOP 'bspline_chain_loop' -- byte assertion
loop = f.edge_loop([oe1, oe2], name="bspline_chain_loop")

# GEOMETRIC_CURVE_SET IS the model entity -- ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
