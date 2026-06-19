"""Gn065 — ConvertSurfaceToBezierBasis BSpline-of-BSpline.

Catalog claim: composite curve where one segment is a TRIMMED BSpline
wrapping another BSpline; Bezier conversion's recursion misclassifies the
wrapped form during basis conversion.

Previous fixture had only one segment, so the "recursion" path wasn't
stressed. Regen with TWO nested TRIMMED_CURVE segments in the COMPOSITE_CURVE
to actually exercise the recursive descent.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn065",
             defect="nested TRIMMED B-spline inside COMPOSITE_CURVE")

# First inner B-spline curve.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 1.0, 0.0))
p2 = f.cartesian_point((2.0, 0.0, 0.0))
inner1 = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('inner1',2,(#{p0.eid},#{p1.eid},#{p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)
trim1 = f._emit_raw(
    f"TRIMMED_CURVE('trim1_wraps_inner1',#{inner1.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(1.0)),.T.,.PARAMETER.)"
)

# Second inner B-spline curve.
p3 = f.cartesian_point((2.0, 0.0, 0.0))
p4 = f.cartesian_point((3.0, -1.0, 0.0))
p5 = f.cartesian_point((4.0, 0.0, 0.0))
inner2 = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('inner2',2,(#{p3.eid},#{p4.eid},#{p5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)
trim2 = f._emit_raw(
    f"TRIMMED_CURVE('trim2_wraps_inner2',#{inner2.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(1.0)),.T.,.PARAMETER.)"
)

# Each TRIMMED_CURVE is wrapped in a COMPOSITE_CURVE_SEGMENT.
seg1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{trim1.eid})")
seg2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{trim2.eid})")

# COMPOSITE_CURVE with both nested-trimmed-bspline segments.
composite = f._emit_raw(
    f"COMPOSITE_CURVE('nested_recursion',(#{seg1.eid},#{seg2.eid}),.F.)"
)

# Minimal carrier so fixture is consumable: wrap as a curve-set representation.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cset',(#{composite.eid}))")
f.add_product_chain(gcs)
