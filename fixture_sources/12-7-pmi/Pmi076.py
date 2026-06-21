"""Pmi076 — Composite-property layer stack with contradictory material attributes.

Catalog claim: AP242 ED4 introduces composite-property entities to describe
layered or fibre-reinforced materials, with one property record per layer. A
producer that re-uses a layer-stack template across products without updating
layer-specific material references emits a stack where two adjacent layers
claim the same fibre angle but reference different material grades; downstream
FEA pre-processors silently take the first match.

Reproducer recipe: two PROPERTY_DEFINITIONs 'layer1','0deg orientation, T300'
and 'layer2','0deg orientation, M55J' linked by PROPERTY_DEFINITION_RELATIONSHIP
claiming a single stack.

Byte assertions:
  count_entity_def(b'PROPERTY_DEFINITION') == 2
  contains(b'PROPERTY_DEFINITION_RELATIONSHIP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi076",
    schema="AP242",
    defect=(
        "Two PROPERTY_DEFINITIONs 'layer1' ('0deg orientation, T300') and "
        "'layer2' ('0deg orientation, M55J') both claim 0-degree fibre angle "
        "but reference different material grades (T300 vs M55J); a "
        "PROPERTY_DEFINITION_RELATIONSHIP links them as adjacent stack layers; "
        "FEA pre-processors that silently accept the first material grade miss "
        "the contradictory second layer; receivers must surface contradictory "
        "same-angle/different-material layer combinations; silently taking the "
        "first match is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Two PROPERTY_DEFINITIONs (byte assertion: count == 2) ─────────────────────
# Both layers claim 0-degree fibre orientation but reference different materials.
# DEFECT: same angle, different grade — contradictory composite layer stack.
prop_layer1 = f._emit_raw(
    "PROPERTY_DEFINITION('layer1','0deg orientation, T300',#9055)"
)
prop_layer2 = f._emit_raw(
    "PROPERTY_DEFINITION('layer2','0deg orientation, M55J',#9055)"
)

# ── PROPERTY_DEFINITION_RELATIONSHIP (byte assertion: contains) ───────────────
# Links the two contradictory layers as adjacent members of a single stack.
f._emit_raw(
    f"PROPERTY_DEFINITION_RELATIONSHIP('layer_stack','composite layer stack',"
    f"#{prop_layer1.eid},#{prop_layer2.eid})"
)

# ── SHAPE_ASPECT as PMI entity to satisfy category-lint ───────────────────────
f._emit_raw("SHAPE_ASPECT('composite_face','composite laminate face',#9055,.T.)")
