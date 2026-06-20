"""Pmi009 — Rounding mode unspecified (ASME banker's vs ISO half-up).

Catalog claim: For 0.5625 displayed at 3 decimals, ASME rounds to 0.562
(banker's) and ISO rounds to 0.563 (half-up). Source and target may both be
"correct" yet show different displayed values. STEP carries no flag indicating
which rule was applied.

Reproducer recipe: Dimension nominal 0.5625 inch, default precision 3 decimals.

Byte assertions:
  contains(b'VALUE_FORMAT_TYPE_QUALIFIER')
  contains(b'PLUS_MINUS_TOLERANCE')
  contains(b'CONVERSION_BASED_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi009",
    defect=(
        "rounding mode unspecified: nominal 0.5625 in at 3 decimals is 0.562 (ASME "
        "banker's) or 0.563 (ISO half-up); STEP carries no flag to disambiguate; "
        "VALUE_FORMAT_TYPE_QUALIFIER('NR2 1.3') present but no rounding-rule UDA; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT,
# #9060=GEOMETRIC_REPRESENTATION_CONTEXT

# ── Inch unit (CONVERSION_BASED_UNIT) ─────────────────────────────────────────
# 1 inch = 25.4 mm; length_unit at #9056 is the SI mm unit.
inch_ctx = f._emit_raw(
    "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#9056)"
)
inch_unit = f._emit_raw(
    f"(CONVERSION_BASED_UNIT('inch',#{inch_ctx.eid})"
    f"NAMED_UNIT(*)LENGTH_UNIT())"
)

# ── Dimensional size ───────────────────────────────────────────────────────────
shape_asp = f._emit_raw("SHAPE_ASPECT('pin_length','',#9055,.T.)")
dim_size = f._emit_raw(f"DIMENSIONAL_SIZE(#{shape_asp.eid},'pin_length')")

# Nominal value: 0.5625 inch (exact in binary, ambiguous at 3 decimal places).
nom_mri = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(0.5625),#{inch_unit.eid})"
)

# VALUE_FORMAT_TYPE_QUALIFIER requests 3 decimal places — does not encode
# whether ASME banker's or ISO half-up rounding must be used.
vftq = f._emit_raw("VALUE_FORMAT_TYPE_QUALIFIER('NR2 1.3')")

# Defect: no rounding-rule UDA; receivers must guess which 3-decimal form is
# "correct" (0.562 or 0.563).
upper_mri = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('upper',LENGTH_MEASURE(0.005),#{inch_unit.eid})"
)
lower_mri = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('lower',LENGTH_MEASURE(0.005),#{inch_unit.eid})"
)
tol_val = f._emit_raw(
    f"TOLERANCE_VALUE(#{upper_mri.eid},#{lower_mri.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tol_val.eid},#{dim_size.eid})"
)
# Intentionally no rounding-rule UDA — that is the defect.
