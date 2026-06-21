"""Gn003 — BSpline curve with empty control_points_list.

Catalog claim: B_SPLINE_CURVE_WITH_KNOTS with an empty control_points_list
(and matching empty knots/multiplicities). Translation throws an exception.
OCCT crashes (signal 11).

Byte assertion: contains(b'B_SPLINE_CURVE')
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn003",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS with empty control_points_list, empty knots, "
        "empty knot_multiplicities; ISO 10303-42 requires at least (degree+1) control "
        "points and a knot vector with at least two distinct values; "
        "OCCT historically threw from RWStepGeom_RWBSplineCurveWithKnots on this; "
        "reject: emit E_EMPTY_BSPLINE_CURVE with offset; continue translating"
    ),
)

# Anchor geometry: CARTESIAN_POINTs so the file is well-formed
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))

# THE DEFECT: B_SPLINE_CURVE_WITH_KNOTS with empty lists
f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('empty',3,(),.UNSPECIFIED.,.F.,.F.,"
    "(),(),.UNSPECIFIED.)"
)
