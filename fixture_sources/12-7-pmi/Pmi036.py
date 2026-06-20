"""Pmi036 — relating_shape_aspect / related_shape_aspect reversed.

Catalog claim: For shape_aspect_relationship between datum_target and feature,
the relating and related roles have been swapped.

Reproducer recipe: shape_aspect_relationship(relating=feature_face,
related=datum_target) where it should be
(relating=datum_target, related=feature_face).

Byte assertions:
  contains(b'PLACED_DATUM_TARGET_FEATURE')
  contains(b'SHAPE_ASPECT_RELATIONSHIP')
  contains(b'SHAPE_ASPECT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi036",
    defect=(
        "SHAPE_ASPECT_RELATIONSHIP has relating and related roles swapped: "
        "relating=feature_face SHAPE_ASPECT, related=PLACED_DATUM_TARGET_FEATURE; "
        "correct encoding requires relating=datum_target, related=feature; "
        "receivers must warn and auto-detect by entity type to repair; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Feature face shape aspect (the non-datum target side).
asp_feature = f._emit_raw("SHAPE_ASPECT('feature_face','',#9055,.T.)")

# Datum target shape aspect and the placed datum target feature.
asp_target = f._emit_raw("SHAPE_ASPECT('datum_target_A','',#9055,.T.)")
pdtf = f._emit_raw(
    f"PLACED_DATUM_TARGET_FEATURE('A1','point',#{asp_target.eid},.T.,'1','A')"
)

# Defect: relating and related are reversed.
# Correct would be: relating=asp_target (datum_target), related=asp_feature (feature).
# Here we encode: relating=asp_feature (feature), related=pdtf (datum_target) — wrong.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('datum link','',#{asp_feature.eid},#{pdtf.eid})"
)
