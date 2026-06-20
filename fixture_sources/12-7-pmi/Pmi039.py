"""Pmi039 — Multiple plus_minus_tolerance on a single dimension.

Catalog claim: More than one PLUS_MINUS_TOLERANCE is associated with the
same DIMENSIONAL_SIZE / DIMENSIONAL_LOCATION.

Reproducer recipe: Two PLUS_MINUS_TOLERANCE entities pointing at the same
DIMENSIONAL_SIZE.

Byte assertions:
  count_entity_def(b'PLUS_MINUS_TOLERANCE') == 2
  count_entity_def(b'TOLERANCE_VALUE') == 2
  contains(b'DIMENSIONAL_SIZE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi039",
    defect=(
        "Two PLUS_MINUS_TOLERANCE entities both point at the same DIMENSIONAL_SIZE; "
        "AP242 RP requires exactly one plus_minus_tolerance per dimensional_size; "
        "receivers must warn and normalize to the first entry deterministically; "
        "silently accepting duplicate tolerances is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Shape aspect for the feature carrying the dimension.
asp = f._emit_raw("SHAPE_ASPECT('hole_feature','',#9055,.T.)")

# Single DIMENSIONAL_SIZE — both tolerances will reference this entity.
dim_size = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp.eid},'diameter')")

# Defect: two TOLERANCE_VALUE entities (byte assertion: count == 2).
tol_val1 = f._emit_raw("TOLERANCE_VALUE(LENGTH_MEASURE(0.05),LENGTH_MEASURE(0.05))")
tol_val2 = f._emit_raw("TOLERANCE_VALUE(LENGTH_MEASURE(0.10),LENGTH_MEASURE(0.10))")

# Defect: two PLUS_MINUS_TOLERANCE entities both attached to the same dim_size.
f._emit_raw(f"PLUS_MINUS_TOLERANCE(#{tol_val1.eid},#{dim_size.eid})")
f._emit_raw(f"PLUS_MINUS_TOLERANCE(#{tol_val2.eid},#{dim_size.eid})")
