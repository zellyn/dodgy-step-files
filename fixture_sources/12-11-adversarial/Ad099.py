"""Ad099 — Self-intersection healing of a wire with self-tangent loop pcurve never terminates.

Catalog claim: a self-intersection-detection pass on a wire whose pcurves
describe a curve that revisits the same parameter range repeatedly (e.g., a
small self-tangent loop) enters an infinite loop because the visited-segment
map keys on segment ID, not segment + direction.

Reproducer recipe: wire whose pcurve traverses a small loop, returning to the
same parameter region multiple times. Self-intersection-fix runs forever.

Byte assertions:
  contains(b'teardrop') or matches(rb'EDGE_CURVE\\([^;]*#(\\d+),#\\1,')
  contains(b'EDGE_LOOP') and contains(b'EDGE_CURVE')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad099",
    defect=(
        "wire whose pcurve traverses a self-tangent teardrop loop; "
        "revisits same parameter range causing self-intersection-fix "
        "to loop forever; visited-segment map keys on ID not ID+direction; "
        "fix must monotonically reduce complexity measure or abort; "
        "OCCT MANTIS#0026671; See also Tsh056; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: a wire with a self-tangent teardrop loop.
#
# The teardrop has a single vertex at the cusp (the self-tangent point).
# An EDGE_CURVE from vertex V back to V (same start and end vertex)
# through a small loop satisfies:
#   matches(rb'EDGE_CURVE\([^;]*#(\d+),#\1,')   — start == end vertex ref
#   contains(b'teardrop')                         — label in entity name
#   contains(b'EDGE_LOOP') and contains(b'EDGE_CURVE')
#
# The pcurve of this loop revisits parameter range [0,2π] twice (the loop
# doubles back), so the self-intersection detector iterates forever.

# Cusp point: the self-tangent meeting point.
cusp_pt = f.cartesian_point((0.5, 0.0, 0.0), name="teardrop_cusp")
cusp_v  = f.vertex_point(cusp_pt)

# Small teardrop loop as a B-spline curve that starts and ends at cusp_pt.
# Control points trace a small loop: cusp → top → right → bottom → cusp.
cp0 = f.cartesian_point((0.5,  0.0,  0.0))   # cusp (start)
cp1 = f.cartesian_point((0.5,  0.1,  0.0))   # upper left
cp2 = f.cartesian_point((0.8,  0.15, 0.0))   # upper right
cp3 = f.cartesian_point((0.8, -0.15, 0.0))   # lower right
cp4 = f.cartesian_point((0.5, -0.1,  0.0))   # lower left
cp5 = f.cartesian_point((0.5,  0.0,  0.0))   # cusp (end = start → self-tangent)

# Degree-3 B-spline, 6 control points → 6+3+1=10 knots (with multiplicities).
# Clamped spline: multiplicity 4 at ends, 1 interior.
loop_curve = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0, cp1, cp2, cp3, cp4, cp5],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.25, 0.75, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,   # declared self-intersecting — triggers the healing pass
    name="teardrop_loop",
)

# EDGE_CURVE from cusp_v back to cusp_v (same vertex → self-tangent loop).
# Satisfies: matches(rb'EDGE_CURVE\([^;]*#(\d+),#\1,')
teardrop_edge = f.edge_curve(cusp_v, cusp_v, loop_curve, same_sense=True,
                              name="teardrop_edge")

# ORIENTED_EDGE wrapping the teardrop edge.
oe = f.oriented_edge(teardrop_edge, True)

# EDGE_LOOP with just the one self-tangent edge.
# Satisfies: contains(b'EDGE_LOOP') and contains(b'EDGE_CURVE')
el = f.edge_loop([oe], name="teardrop_wire_loop")

# Second self-tangent loop at a different location (exercises multi-loop path).
cusp2_pt = f.cartesian_point((2.0, 0.0, 0.0), name="teardrop_cusp2")
cusp2_v  = f.vertex_point(cusp2_pt)

cp6 = f.cartesian_point((2.0,  0.0,  0.0))
cp7 = f.cartesian_point((2.0,  0.05, 0.0))
cp8 = f.cartesian_point((2.1,  0.08, 0.0))
cp9 = f.cartesian_point((2.1, -0.08, 0.0))
cp10 = f.cartesian_point((2.0, -0.05, 0.0))
cp11 = f.cartesian_point((2.0,  0.0,  0.0))

loop_curve2 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp6, cp7, cp8, cp9, cp10, cp11],
    knot_multiplicities=[4, 1, 1, 4],
    knots=[0.0, 0.25, 0.75, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=True,
    name="teardrop_loop2",
)

teardrop_edge2 = f.edge_curve(cusp2_v, cusp2_v, loop_curve2, same_sense=True,
                               name="teardrop_edge2")
oe2 = f.oriented_edge(teardrop_edge2, True)
f.edge_loop([oe2], name="teardrop_wire_loop2")
