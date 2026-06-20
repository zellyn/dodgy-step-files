"""Pmi024 — Illegal characters inside a UUID value.

Catalog claim: UUID string contains characters outside [0-9a-f-].

Reproducer recipe: UUID_ATTRIBUTE('4ce0ACF8-1a2b-4c3d-9e8f-7a6b5c4dXYZ')

Byte assertions:
  contains(b'UUID_ATTRIBUTE')
  contains(b'XYZ')
  matches(rb"'4ce0ACF8-1a2b-4c3d-9e8f-7a6b5c4dXYZ'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi024",
    defect=(
        "UUID_ATTRIBUTE value '4ce0ACF8-1a2b-4c3d-9e8f-7a6b5c4dXYZ' contains "
        "uppercase hex digits (ACF8) and non-hex suffix (XYZ); AP242 UUID values "
        "must match [0-9a-f-] only; receivers must warn and not attempt to repair; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# A single shape aspect to receive the malformed UUID.
asp = f._emit_raw("SHAPE_ASPECT('feature_a','',#9055,.T.)")

# Defect: UUID value contains uppercase hex and non-hex characters (ACF8, XYZ).
# AP242 §4.x: all UUID characters must be drawn from [0-9a-f-].
f._emit_raw(
    f"UUID_ATTRIBUTE('4ce0ACF8-1a2b-4c3d-9e8f-7a6b5c4dXYZ',#{asp.eid})"
)
