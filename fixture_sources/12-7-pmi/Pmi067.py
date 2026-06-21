"""Pmi067 — 'INCH' named differently on conversion_based_unit.

Catalog claim: The conventional name for inches in PMI dimensional measurements
is 'INCH'; producers sometimes write 'inch', 'IN', or 'inches', breaking PMI
value display.

Reproducer recipe: CONVERSION_BASED_UNIT with name 'inches' instead of 'INCH',
converting 25.4 millimetres.

Byte assertions:
  contains(b'CONVERSION_BASED_UNIT') or contains(b'INCH')
  contains(b'DIMENSIONAL_EXPONENTS')
  contains(b'PLUS_MINUS_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi067",
    defect=(
        "CONVERSION_BASED_UNIT uses name 'inches' instead of the conventional "
        "'INCH'; the AP242 PMI display pipeline matches the unit name case-sensitively "
        "and does not recognize 'inches', 'inch', or 'IN' as valid inch spellings; "
        "PMI dimensional values referencing this unit display incorrectly; "
        "receivers must case-insensitively normalize inch unit names and emit a "
        "warning on case-form mismatch; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT (mm SI)

# ── DIMENSIONAL_EXPONENTS for a length unit (L^1) ────────────────────────────
dim_exp = f._emit_raw(
    "DIMENSIONAL_EXPONENTS(1.0,0.0,0.0,0.0,0.0,0.0,0.0)"
)

# ── SI millimetre named unit (basis for conversion) ───────────────────────────
si_mm = f._emit_raw(
    "(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))"
)

# ── LENGTH_MEASURE_WITH_UNIT: 25.4 millimetres ────────────────────────────────
lm_25_4 = f._emit_raw(
    f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#{si_mm.eid})"
)

# ── CONVERSION_BASED_UNIT: name is 'inches' — DEFECT (should be 'INCH') ──────
# The (CONVERSION_BASED_UNIT()LENGTH_UNIT()NAMED_UNIT(*)) complex form.
inch_unit = f._emit_raw(
    f"(CONVERSION_BASED_UNIT('inches',#{lm_25_4.eid})"
    f"LENGTH_UNIT()NAMED_UNIT(#{dim_exp.eid}))"
)

# ── Shape aspect for a toleranced dimension ───────────────────────────────────
tol_aspect = f._emit_raw(
    "SHAPE_ASPECT('toleranced_width','',#9055,.T.)"
)

# ── DIMENSIONAL_SIZE referencing the aspect ───────────────────────────────────
ds = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{tol_aspect.eid},'width')"
)

# ── PLUS_MINUS_TOLERANCE with values in the misspelled inch unit ──────────────
mri_nom = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(2.0),#{inch_unit.eid})"
)
mri_upper = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('upper',LENGTH_MEASURE(0.005),#{inch_unit.eid})"
)
mri_lower = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('lower',LENGTH_MEASURE(0.005),#{inch_unit.eid})"
)
tol_val = f._emit_raw(
    f"TOLERANCE_VALUE(#{mri_upper.eid},#{mri_lower.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tol_val.eid},#{ds.eid})"
)
