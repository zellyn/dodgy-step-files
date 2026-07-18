"""Pmi054 — basis_curve for leader/annotation not on allowed list.

Catalog claim: Annotation polyline / trimmed_curve references a basis curve
not on the allowed list (lines, circles, polylines).

Reproducer recipe: Annotation polyline whose basis curve is a
b_spline_curve_with_knots.

Byte assertions:
  contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'PRESENTATION_STYLE_ASSIGNMENT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi054",
    defect=(
        "ANNOTATION_CURVE_OCCURRENCE references a B_SPLINE_CURVE_WITH_KNOTS as its "
        "basis curve; the AP242 RP restricts annotation leader/basis curves to the "
        "allowed set {line, circle, polyline}; using an unsupported basis curve type "
        "is non-conformant; receivers must warn and coerce to best-effort render; "
        "must not crash on the rendering path; "
        "the defect is a presentation/PMI property the shape-count oracles cannot observe, and here it also sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# B_SPLINE_CURVE_WITH_KNOTS as the (disallowed) basis curve for the annotation.
# A simple quadratic b-spline through three control points.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((5.0, 5.0, 0.0))
cp2 = f.cartesian_point((10.0, 0.0, 0.0))
bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('leader_basis',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.PIECEWISE_BEZIER_KNOTS.)"
)

# ANNOTATION_CURVE_OCCURRENCE wrapping the b-spline (the defect).
colour = f._emit_raw("COLOUR_RGB('anno_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)
f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader',(#{bspline.eid}),#{psa.eid})"
)
