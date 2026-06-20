"""Pmi023 — Multiple UUIDs for the same identified_item.

Catalog claim: Two uuid_attribute entries reference the same item with different
UUID values, creating ambiguity for round-trip.

Reproducer recipe: Two UUID_ATTRIBUTE entries pointing to the same shape with
different values.

Byte assertions:
  count_entity_def(b'UUID_ATTRIBUTE') == 2
  contains(b'4ce0acf8-1a2b-4c3d-9e8f-7a6b5c4d3e2f')
  contains(b'a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi023",
    defect=(
        "two UUID_ATTRIBUTE entities point to the same SHAPE_ASPECT with different "
        "UUID values ('4ce0acf8-…' and 'a1b2c3d4-…'); creates round-trip ambiguity; "
        "receivers must warn and normalise deterministically (lex-sort first); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# A single shape aspect that becomes the identified_item.
asp = f._emit_raw("SHAPE_ASPECT('feature_a','',#9055,.T.)")

# Defect: two UUID_ATTRIBUTE entries both pointing to the same asp — different
# UUID values produce ambiguity about which is the canonical identifier.
f._emit_raw(
    f"UUID_ATTRIBUTE('4ce0acf8-1a2b-4c3d-9e8f-7a6b5c4d3e2f',#{asp.eid})"
)
f._emit_raw(
    f"UUID_ATTRIBUTE('a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d',#{asp.eid})"
)
