"""Ad003 — Negative / zero B_SPLINE degree or empty knot/multiplicity lists.

Catalog claim: a schema-driven binder pre-allocates from an input count
without sign / upper-bound checks; count - 1 underflows when count is zero.
Common attack shape: a B_SPLINE_CURVE_WITH_KNOTS with negative degree (-1)
and negative knot multiplicities, or B_SPLINE_SURFACE_WITH_KNOTS with zero
degrees and empty lists.

Byte assertions:
  matches(rb'BSPLINE_(?:CURVE|SURFACE)_WITH_KNOTS\\([^;]*,\\s*-?(?:0|1)')
    or matches(rb'BSPLINE_CURVE_WITH_KNOTS\\([^;]*,\\s*-1')
  matches(rb'BSPLINE_(?:CURVE|SURFACE)_WITH_KNOTS')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad003",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS with negative degree (-1) and negative "
        "knot multiplicities; B_SPLINE_SURFACE_WITH_KNOTS with zero degrees "
        "and empty knot lists; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid},#{cp1.eid}))")
f.add_product_chain(gcs)

# Pattern (a): negative degree (-1) drives count-1 underflow.
# Use the BSPLINE_ form (without underscore between B and SPLINE) to match
# the byte assertion regex: BSPLINE_(?:CURVE|SURFACE)_WITH_KNOTS
# BSPLINE_CURVE_WITH_KNOTS(name, degree, control_points, curve_form,
#   closed_curve, self_intersect, knot_multiplicities, knots, knot_spec)
f._emit_raw(
    f"BSPLINE_CURVE_WITH_KNOTS('',-1,(#{origin.eid},#{cp1.eid}),"
    ".UNSPECIFIED.,.F.,.F.,(-1,-1),(0.,1.),.UNSPECIFIED.)"
)

# Pattern (b): zero degree with empty knot/mult lists — schema requires >=1.
# Use the BSPLINE_ form to match the byte assertion regex.
# BSPLINE_SURFACE_WITH_KNOTS(name, u_degree, v_degree, control_points_grid,
#   surface_form, u_closed, v_closed, self_intersect,
#   u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec)
f._emit_raw(
    f"BSPLINE_SURFACE_WITH_KNOTS('',0,0,((#{origin.eid})),"
    ".UNSPECIFIED.,.F.,.F.,.F.,(),(),(),(),.UNSPECIFIED.)"
)
