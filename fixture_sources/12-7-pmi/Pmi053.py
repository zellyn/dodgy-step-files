"""Pmi053 — annotation_curve_occurrence leader with single point.

Catalog claim: An annotation_curve_occurrence representing a leader contains
exactly one point in its polyline rather than >=2.

Reproducer recipe: Leader polyline with one vertex.

Byte assertions:
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'POLYLINE')
  contains(b'CURVE_STYLE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi053",
    defect=(
        "ANNOTATION_CURVE_OCCURRENCE leader contains a POLYLINE with exactly one "
        "point; a valid leader requires >=2 points to define a line segment; "
        "a single-point polyline is degenerate and receivers must warn and drop "
        "the leader; silently accepting a degenerate single-point leader is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect: POLYLINE with exactly one point — degenerate leader.
pt_only = f.cartesian_point((5.0, 5.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_only.eid}))"
)

# Presentation style (CURVE_STYLE byte assertion satisfied).
colour = f._emit_raw("COLOUR_RGB('anno_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)

# The annotation curve occurrence referencing the single-point (degenerate) polyline.
f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader',(#{polyline.eid}),#{psa.eid})"
)
