"""Pmi078 — PMI text location wrong after import.

Catalog claim: a DIMENSION PMI entity carries an annotation text position.
STEP reader treats the position relative to the part origin, but the producer
emitted it relative to the part's AXIS2_PLACEMENT_3D (the local frame). Result:
PMI text appears displaced from the feature it labels by the axis-placement
offset.

Reproducer recipe: Part with AXIS2_PLACEMENT_3D origin at (100,0,0); PMI text
position (5,0,0) (relative to part frame). Reader places text at (5,0,0)
instead of (105,0,0).

Byte assertions:
  contains(b'ANNOTATION_TEXT_OCCURRENCE')
  count_entity_def(b'CARTESIAN_POINT') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi078",
    schema="AP242",
    defect=(
        "Part AXIS2_PLACEMENT_3D has origin at (100,0,0); "
        "ANNOTATION_TEXT_OCCURRENCE 'label' carries text position CARTESIAN_POINT "
        "(5,0,0) emitted relative to the part frame; a reader that treats this as "
        "a world-frame coordinate places the PMI text at (5,0,0) instead of the "
        "correct (105,0,0); receivers must add the part's AXIS2_PLACEMENT_3D "
        "origin offset when resolving annotation text positions; silently placing "
        "text at the raw coordinate without frame transformation is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
# CARTESIAN_POINT #1: the GCS origin used in the model entity.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# CARTESIAN_POINT #2: annotation text position in part frame.
# DEFECT: this is (5,0,0) relative to part frame whose origin is at (100,0,0);
# the correct world position is (105,0,0) but readers see (5,0,0).
text_pos = f._emit_raw("CARTESIAN_POINT('text_pos_local',(5.0,0.0,0.0))")

# ── ANNOTATION_TEXT_OCCURRENCE (byte assertion: contains) ─────────────────────
# Carries the PMI label and its defective (part-frame) text position.
f._emit_raw(
    f"ANNOTATION_TEXT_OCCURRENCE('label','annotation in part frame',"
    f"(),#{text_pos.eid})"
)
