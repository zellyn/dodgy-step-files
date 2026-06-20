"""Pmi048 — Graphic PMI annotation missing color.

Catalog claim: An annotation_curve_occurrence carries no
presentation_style_assignment color, so receivers must default.

Reproducer recipe: annotation_curve_occurrence with no styled_item chain.

Byte assertions:
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  count_entity_def(b'COLOUR_RGB') == 0
  count_entity_def(b'STYLED_ITEM') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi048",
    defect=(
        "ANNOTATION_CURVE_OCCURRENCE has no PRESENTATION_STYLE_ASSIGNMENT color binding; "
        "no STYLED_ITEM or COLOUR_RGB entity is present; receivers must default to a "
        "documented color (e.g. black) and warn; silently accepting a colorless annotation "
        "without a diagnostic is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Graphic polyline for the annotation body.
pt_a = f.cartesian_point((0.0, 0.0, 0.0))
pt_b = f.cartesian_point((10.0, 0.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)

# Defect: ANNOTATION_CURVE_OCCURRENCE with NO presentation_style_assignment ($).
# No STYLED_ITEM, no COLOUR_RGB, no CURVE_STYLE — the color is completely missing.
f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader',(#{polyline.eid}),$)"
)
