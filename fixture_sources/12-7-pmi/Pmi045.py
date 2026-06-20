"""Pmi045 — Graphic-only PMI with no semantic backing.

Catalog claim: PMI is exported only as polylines / annotation_curve_occurrence
(graphic presentation) with no parallel semantic representation. Looks correct
visually but cannot be consumed by inspection / CMM / machining downstream.

Reproducer recipe: AP203/AP214 file with draughting_callout containing only
annotation_curve_occurrences and no dimensional_size / geometric_tolerance
semantic counterpart.

Byte assertions:
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'COLOUR_RGB')
  contains(b'STYLED_ITEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi045",
    defect=(
        "PMI exported as ANNOTATION_CURVE_OCCURRENCE graphic polyline only; "
        "no DIMENSIONAL_SIZE or GEOMETRIC_TOLERANCE semantic counterpart is present; "
        "graphic-presentation-only PMI looks correct visually but cannot be consumed "
        "by inspection / CMM / machining downstream; receivers must coerce to a "
        "'graphic only' flag and warn; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Graphic polyline representing the annotation leader / callout.
pt_a = f.cartesian_point((10.0, 0.0, 0.0))
pt_b = f.cartesian_point((20.0, 0.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)

# ANNOTATION_CURVE_OCCURRENCE wrapping the polyline (graphic PMI entity).
anno_curve = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('leader',(#{polyline.eid}),$)"
)

# Color and styled item so OCC/gmsh can render it visually.
colour = f._emit_raw("COLOUR_RGB('annotation_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)
# STYLED_ITEM binds the graphic style to the annotation curve occurrence.
f._emit_raw(
    f"STYLED_ITEM('',(#{psa.eid}),#{anno_curve.eid})"
)

# Draughting callout with the annotation — no semantic DIMENSIONAL_SIZE or
# GEOMETRIC_TOLERANCE entity is present: that is the defect.
f._emit_raw(
    f"DRAUGHTING_CALLOUT('pmi_callout',(#{anno_curve.eid}))"
)
