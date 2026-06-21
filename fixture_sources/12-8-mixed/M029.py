"""M029 — PMI-count validation property failure.

Catalog claim: The number of GD&T tolerances / datum features is embedded as a
validation property (INTEGER_REPRESENTATION_ITEM inside PROPERTY_DEFINITION); the
receiver reports a different count after import because some PMI was tagged as
graphic-only and dropped, or because composite callouts were exploded.

Reproducer recipe: 12 PMI annotations declared in validation_property; 10 imported.

Byte assertions:
  contains(b'INTEGER_REPRESENTATION_ITEM')
  contains(b'PROPERTY_DEFINITION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M029",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing PMI-count validation property encoded as "
        "INTEGER_REPRESENTATION_ITEM inside PROPERTY_DEFINITION; "
        "input: AP242 STEP file where 12 PMI annotations are declared in a "
        "validation_property but only 10 survive import (2 dropped as graphic-only "
        "or exploded from composite callouts); "
        "LOTAR/CAx-IF validation: receiver compares declared count to imported count "
        "and must reject or emit diagnostic when they differ; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: PMI count validation fails, validation property fails check, "
        "GD&T count mismatch on import, tolerance count differs after read"
    ),
)

# ── PMI annotation count validation property ──────────────────────────────────
# Byte assertion: contains(b'INTEGER_REPRESENTATION_ITEM')
# Byte assertion: contains(b'PROPERTY_DEFINITION')

# 12 annotations declared in the validation property
pmi_count = f._emit_raw(
    "INTEGER_REPRESENTATION_ITEM('number_of_annotations',12)"
)

# PROPERTY_DEFINITION encoding the declared PMI count
# Byte assertion: contains(b'PROPERTY_DEFINITION')
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_validation_property',"
    f"'declared PMI count: 12 annotations',$)"
)

# PROPERTY_DEFINITION_REPRESENTATION ties the count to the property
prop_rep = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{pmi_count.eid})"
)

# Simulate 12 individual PMI annotation placeholders declared in the file
# (in practice some would be graphic-only or composite — 2 will be dropped on import)
annot_ids = []
for i in range(1, 13):
    a = f._emit_raw(
        f"VALUE_REPRESENTATION_ITEM('annotation_{i:02d}',MEASURE_VALUE({i * 10.0}))"
    )
    annot_ids.append(a)

# Composite callout that gets exploded into sub-annotations during import
# (this is one source of the count discrepancy)
composite = f._emit_raw(
    f"COMPOUND_REPRESENTATION_ITEM('composite_gdt_callout',"
    f"(#{annot_ids[10].eid},#{annot_ids[11].eid}))"
)

# Graphic-only annotation (tagged so it should not be counted, but declared above)
graphic_only = f._emit_raw(
    "VALUE_REPRESENTATION_ITEM('graphic_only_flag',MEASURE_VALUE(1.))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('pmi-count-validation-property-failure',"
    f"(#{pmi_count.eid},#{prop_def.eid},#{prop_rep.eid},#{composite.eid},"
    f"#{graphic_only.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M029.stp")
