"""Pmi012 — Identical id_attribute reused across shape_aspect /
dimensional_location / dimensional_size / shape_aspect_relationship.

Catalog claim: AP242 imposes a global uniqueness rule on the derived id
attribute across shape_aspect, dimensional_location, dimensional_size, and
shape_aspect_relationship. Writers that scope IDs per-entity-type produce
conflicting IDs that violate the rule.

Reproducer recipe: File with id_attribute('A1', shape_aspect#1) and
id_attribute('A1', dimensional_location#2) and id_attribute('A1',
dimensional_size#3).

Byte assertions:
  count_entity_def(b'ID_ATTRIBUTE') == 3
  contains(b'DIMENSIONAL_SIZE')
  contains(b'DIMENSIONAL_LOCATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi012",
    defect=(
        "id_attribute 'A1' reused on SHAPE_ASPECT, DIMENSIONAL_LOCATION, and "
        "DIMENSIONAL_SIZE — AP242 requires global uniqueness across all four "
        "entity types; writers that scope IDs per-type produce collisions; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Two shape aspects for use in the dimensional entities.
asp1 = f._emit_raw("SHAPE_ASPECT('feature_a','',#9055,.T.)")
asp2 = f._emit_raw("SHAPE_ASPECT('feature_b','',#9055,.T.)")

# Dimensional entities sharing the same textual id 'A1'.
dim_loc = f._emit_raw(
    f"DIMENSIONAL_LOCATION('A1','length between features',#{asp1.eid},#{asp2.eid})"
)
dim_size = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp1.eid},'A1')"
)

# Defect: three ID_ATTRIBUTE instances all carrying 'A1'.
# Each writer scoped IDs per entity type and did not check the cross-type
# uniqueness rule.
f._emit_raw(f"ID_ATTRIBUTE('A1',#{asp1.eid})")
f._emit_raw(f"ID_ATTRIBUTE('A1',#{dim_loc.eid})")
f._emit_raw(f"ID_ATTRIBUTE('A1',#{dim_size.eid})")
# Intentionally three colliding IDs — that is the defect.
