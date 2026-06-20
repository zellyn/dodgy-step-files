"""Pmi034 — placed_datum_target_feature shared DatumTargetType_Area null deref.

Catalog claim: Incorrect sharing of DatumTargetType_Area instance across
multiple PLACED_DATUM_TARGET_FEATUREs causes NULL dereference during
translation.

Reproducer recipe: AP242 file with two placed_datum_target_features sharing
one DatumTargetType_Area entity (via a single DESCRIPTIVE_REPRESENTATION_ITEM
that both features reference through PROPERTY_DEFINITION_REPRESENTATION).

Byte assertions:
  count_entity_def(b'PLACED_DATUM_TARGET_FEATURE') == 2
  count_entity_def(b'PROPERTY_DEFINITION') == 2
  contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi034",
    defect=(
        "Two PLACED_DATUM_TARGET_FEATUREs share a single DESCRIPTIVE_REPRESENTATION_ITEM "
        "encoding the DatumTargetType_Area; incorrect sharing causes NULL dereference "
        "during translation in OCC; receivers must maintain independent target-type "
        "instances with null-guards on every reference; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Two datum feature shape aspects.
asp_a = f._emit_raw("SHAPE_ASPECT('datum_feature_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('datum_feature_B','',#9055,.T.)")

# Two PLACED_DATUM_TARGET_FEATUREs — the defect: both share one area type item.
# Arguments: name, description, of_shape, product_definitional, target_id, target_label
pdtf_a = f._emit_raw(
    f"PLACED_DATUM_TARGET_FEATURE('A1','area',#{asp_a.eid},.T.,'1','A')"
)
pdtf_b = f._emit_raw(
    f"PLACED_DATUM_TARGET_FEATURE('B1','area',#{asp_b.eid},.T.,'1','B')"
)

# Defect: a single shared DESCRIPTIVE_REPRESENTATION_ITEM for DatumTargetType_Area.
# Both features reference the same instance — this triggers the null deref.
shared_type = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('datum target type','area')"
)

# Shared representation wrapping the single type item.
shared_rep = f._emit_raw(
    f"REPRESENTATION('',(#{shared_type.eid}),$)"
)

# Two PROPERTY_DEFINITIONs (satisfies count_entity_def == 2) pointing at each
# feature but both pointing at the same representation — the shared-instance defect.
prop_def_a = f._emit_raw(
    f"PROPERTY_DEFINITION('datum target type','',#{pdtf_a.eid})"
)
prop_def_b = f._emit_raw(
    f"PROPERTY_DEFINITION('datum target type','',#{pdtf_b.eid})"
)

f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def_a.eid},#{shared_rep.eid})"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def_b.eid},#{shared_rep.eid})"
)
