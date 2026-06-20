"""Pmi022 — Duplicate UUID on multiple identified_item.

Catalog claim: Same UUID string attached via uuid_attribute to two different
identified_item entities. Violates uniqueness.

Reproducer recipe: Two UUID_ATTRIBUTE entities reference different shape items
but share '4ce0acf8-1a2b-4c3d-9e8f-7a6b5c4d3e2f'.

Byte assertions:
  count_entity_def(b'UUID_ATTRIBUTE') == 2
  count(b'4ce0acf8-1a2b-4c3d-9e8f-7a6b5c4d3e2f') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi022",
    defect=(
        "same UUID '4ce0acf8-1a2b-4c3d-9e8f-7a6b5c4d3e2f' bound via UUID_ATTRIBUTE "
        "to two different identified_item entities; violates AP242 uniqueness rule; "
        "receivers must warn and apply a consistent keep-first-or-last policy; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# Two distinct shape aspects — each will become a separate identified_item.
asp1 = f._emit_raw("SHAPE_ASPECT('feature_a','',#9055,.T.)")
asp2 = f._emit_raw("SHAPE_ASPECT('feature_b','',#9055,.T.)")

# Defect: both UUID_ATTRIBUTE entities carry the identical UUID string.
# AP242 ed≥4 §xxx: uuid_attribute values must be unique across all
# identified_item instances within a product.
uuid_val = "'4ce0acf8-1a2b-4c3d-9e8f-7a6b5c4d3e2f'"
f._emit_raw(f"UUID_ATTRIBUTE({uuid_val},#{asp1.eid})")
f._emit_raw(f"UUID_ATTRIBUTE({uuid_val},#{asp2.eid})")
