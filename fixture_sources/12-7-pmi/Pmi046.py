"""Pmi046 — characterized_object with non-PMI draughting subtypes for graphic PMI.

Catalog claim: Producer used (characterized_object)(draughting_callout) or
draughting_annotation_*_occurrence instead of the AP242 RP-prescribed
annotation_curve_occurrence.

Reproducer recipe: Annotation written as complex
(characterized_object)(draughting_callout).

Byte assertions:
  contains(b'DRAUGHTING_ANNOTATION_OCCURRENCE')
  contains(b'PRESENTATION_STYLE_ASSIGNMENT')
  contains(b'COLOUR_RGB')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi046",
    defect=(
        "Annotation encoded as DRAUGHTING_ANNOTATION_OCCURRENCE instead of the "
        "AP242 RP-required ANNOTATION_CURVE_OCCURRENCE; using a non-PMI draughting "
        "subtype for graphic PMI is non-conformant; receivers must warn and reject; "
        "silently accepting the wrong subtype is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Graphic polyline for the annotation body.
pt_a = f.cartesian_point((5.0, 0.0, 0.0))
pt_b = f.cartesian_point((15.0, 0.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)

# Color and presentation style (byte assertions).
colour = f._emit_raw("COLOUR_RGB('anno_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)

# Defect: DRAUGHTING_ANNOTATION_OCCURRENCE used instead of
# ANNOTATION_CURVE_OCCURRENCE — wrong draughting subtype for graphic PMI.
# AP242 RP §12 requires annotation_curve_occurrence for graphic PMI;
# draughting_annotation_occurrence is a non-PMI draughting entity class.
dao = f._emit_raw(
    f"DRAUGHTING_ANNOTATION_OCCURRENCE('callout',(#{polyline.eid}),#{psa.eid})"
)

# Complex (characterized_object)(draughting_callout) wrapper — the RP
# non-conformant pattern named in the catalog entry.
f._emit_raw(
    f"(CHARACTERIZED_OBJECT('callout_co','')(DRAUGHTING_CALLOUT('pmi_dc',(#{dao.eid}))))"
)
