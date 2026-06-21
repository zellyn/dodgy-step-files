"""M031 — Validation property: missing unit_component.

Catalog claim: A geometric/validation property has values but no unit_component,
leaving units unspecified. This violates the CAx-IF RP requirement that every
length/area/volume measure carry an explicit unit reference.

Reproducer recipe: GVP with length_measure value but no associated unit reference.

Byte assertions:
  contains(b'MEASURE_REPRESENTATION_ITEM')
  matches(rb'LENGTH_MEASURE\\(123.45\\),\\$')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M031",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing MEASURE_REPRESENTATION_ITEM with "
        "LENGTH_MEASURE(123.45) and no unit_component ($); "
        "input: AP242 STEP file where a geometric validation property has a "
        "length_measure value but the unit_component field is $ (unset), "
        "leaving units unspecified; "
        "CAx-IF RP requires every measure to carry an explicit unit reference; "
        "kernel must warn; archive-reject if strict; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: GVP missing unit_component, validation property no units, "
        "validation value with no unit, unit_component absent on property"
    ),
)

# ── MEASURE_REPRESENTATION_ITEM with missing unit_component ($) ───────────────
# Byte assertion: contains(b'MEASURE_REPRESENTATION_ITEM')
# Byte assertion: matches(rb'LENGTH_MEASURE\(123.45\),\$')
# The third argument (unit_component) is $ — absent/unspecified
mri = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('edge_length',LENGTH_MEASURE(123.45),$)"
)

# PROPERTY_DEFINITION for the validation property
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('geometric validation property',"
    f"'edge length without unit',$)"
)

# PROPERTY_DEFINITION_REPRESENTATION ties the unitless measure to the property
prop_rep = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{mri.eid})"
)

# A second measure with the same defect — area with no unit
mri_area = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('bounding_area',AREA_MEASURE(56.78),$)"
)

prop_def2 = f._emit_raw(
    f"PROPERTY_DEFINITION('geometric validation property',"
    f"'bounding area without unit',$)"
)

prop_rep2 = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def2.eid},#{mri_area.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gvp-missing-unit-component',"
    f"(#{mri.eid},#{prop_def.eid},#{prop_rep.eid},"
    f"#{mri_area.eid},#{prop_def2.eid},#{prop_rep2.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M031.stp")
