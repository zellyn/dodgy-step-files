"""M030 — Validation property naming: "geometric_validation_property" with underscores vs spaces.

Catalog claim: Validation-property recommended-practices name changed
(geometric_validation_property → geometric validation property); both forms appear
in the wild. The underscore form is non-conforming after the RP change.

Reproducer recipe: PROPERTY_DEFINITION named with the underscore form.

Byte assertions:
  contains(b"PROPERTY_DEFINITION('geometric_validation_property'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M030",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing PROPERTY_DEFINITION named "
        "'geometric_validation_property' (underscore form); "
        "input: AP242 STEP file where validation-property RP name changed from "
        "'geometric_validation_property' to 'geometric validation property' (space form); "
        "the underscore form is written by older CAD tools that predate the RP update; "
        "kernel must heal: replace underscore with space before comparison, "
        "or accept both name forms as equivalent; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: GVP name underscore vs space, validation property naming inconsistent, "
        "geometric_validation_property naming form, RP changed name format"
    ),
)

# ── Volume measurement value ──────────────────────────────────────────────────
vol_measure = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('volume',VOLUME_MEASURE(1234.567),"
    "(SI_UNIT(.MILLI.,.METRE.) LENGTH_UNIT() NAMED_UNIT(*)))"
)

# ── PROPERTY_DEFINITION with underscore form — the non-conforming name ────────
# Byte assertion: contains(b"PROPERTY_DEFINITION('geometric_validation_property'")
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('geometric_validation_property',"
    f"'volume in cubic mm',$)"
)

# PROPERTY_DEFINITION_REPRESENTATION ties the value to the property
prop_rep = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{vol_measure.eid})"
)

# Also include the correct space form to show contrast
prop_def_correct = f._emit_raw(
    f"PROPERTY_DEFINITION('geometric validation property',"
    f"'area in square mm',$)"
)

area_measure = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('surface_area',AREA_MEASURE(456.789),"
    "(SI_UNIT(.MILLI.,.METRE.) LENGTH_UNIT() NAMED_UNIT(*)))"
)

prop_rep_correct = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def_correct.eid},#{area_measure.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gvp-name-underscore-vs-space',"
    f"(#{vol_measure.eid},#{prop_def.eid},#{prop_rep.eid},"
    f"#{prop_def_correct.eid},#{area_measure.eid},#{prop_rep_correct.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M030.stp")
