"""M032 — Validation property name not in CAx-IF list / mismatches associated general_property name.

Catalog claim: property_definition.name does not match a recognized CAx-IF
validation-property keyword, or a user-defined-attribute general_property.name
differs from the linked property_definition.name.

Reproducer recipe: GVP whose name is 'volume mm3' instead of 'volume'.

Byte assertions:
  contains(b'volume mm3')
  contains(b'GENERAL_PROPERTY')
  contains(b"'Volume'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M032",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing PROPERTY_DEFINITION named 'volume mm3' "
        "(non-standard CAx-IF name) with associated GENERAL_PROPERTY named 'Volume'; "
        "input: AP242 STEP file where property_definition.name is 'volume mm3' instead "
        "of the CAx-IF recognized keyword 'volume'; also general_property.name 'Volume' "
        "differs from the linked property_definition.name 'volume mm3'; "
        "kernel must warn and accept: emit diagnostic on unrecognized name, "
        "ignore or log non-standard validation property; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: GVP name not in CAx-IF list, validation property name unrecognized, "
        "general_property name mismatch, non-standard validation property name"
    ),
)

# ── Volume measure with standard units ────────────────────────────────────────
vol_measure = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('volume',VOLUME_MEASURE(98765.4),"
    "(SI_UNIT(.MILLI.,.METRE.) LENGTH_UNIT() NAMED_UNIT(*)))"
)

# ── GENERAL_PROPERTY with name 'Volume' (capital V — mismatches property_definition) ──
# Byte assertion: contains(b"'Volume'")
# Byte assertion: contains(b'GENERAL_PROPERTY')
gen_prop = f._emit_raw(
    "GENERAL_PROPERTY('Volume','user-defined volume attribute',$)"
)

# ── PROPERTY_DEFINITION with non-standard name 'volume mm3' ──────────────────
# Byte assertion: contains(b'volume mm3')
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('volume mm3',"
    f"'non-standard CAx-IF validation property name',#{gen_prop.eid})"
)

# PROPERTY_DEFINITION_REPRESENTATION ties the measure to the property
prop_rep = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{vol_measure.eid})"
)

# Second example: 'area sqmm' instead of 'area'
area_measure = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('area',AREA_MEASURE(4321.0),"
    "(SI_UNIT(.MILLI.,.METRE.) LENGTH_UNIT() NAMED_UNIT(*)))"
)

gen_prop2 = f._emit_raw(
    "GENERAL_PROPERTY('Area','user-defined area attribute',$)"
)

prop_def2 = f._emit_raw(
    f"PROPERTY_DEFINITION('area sqmm',"
    f"'non-standard area name',#{gen_prop2.eid})"
)

prop_rep2 = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def2.eid},#{area_measure.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gvp-name-not-in-caxif-list',"
    f"(#{vol_measure.eid},#{gen_prop.eid},#{prop_def.eid},#{prop_rep.eid},"
    f"#{area_measure.eid},#{gen_prop2.eid},#{prop_def2.eid},#{prop_rep2.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M032.stp")
