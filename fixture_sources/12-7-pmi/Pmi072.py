"""Pmi072 — DIMENSION_PAIR with mismatched units between paired members.

Catalog claim: AP242 DIMENSION_PAIR couples two dimensions that are
conceptually the same measurement. A producer that sources one half from an
inch-based legacy CAD library and the other from a millimetre-based current
export emits the pair with mixed units. The pair is mathematically inconsistent
unless the receiver normalises units before comparing.

Reproducer recipe: DIMENSION_PAIR('width','height'); width
MEASURE_REPRESENTATION_ITEM in mm; height MEASURE_REPRESENTATION_ITEM in
inches via CONVERSION_BASED_UNIT.

Byte assertions:
  contains(b'DIMENSION_PAIR')
  count_entity_def(b'DIMENSIONAL_SIZE') == 2
  contains(b'DIMENSIONAL_EXPONENTS')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi072",
    schema="AP242",
    defect=(
        "DIMENSION_PAIR couples two DIMENSIONAL_SIZE entities with mismatched units: "
        "'width' uses MEASURE_REPRESENTATION_ITEM in millimetres (#9056) while "
        "'height' uses a CONVERSION_BASED_UNIT for inches (25.4mm); the pair is "
        "mathematically inconsistent without unit normalisation; receivers must "
        "convert both halves to a canonical unit before comparison and warn on "
        "mismatched units; silently treating both values as if in the same unit "
        "is forbidden; "
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

# ── Inch unit via CONVERSION_BASED_UNIT ──────────────────────────────────────
inch_ctx = f._emit_raw(
    "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#9056)"
)
inch_unit = f._emit_raw(
    f"(CONVERSION_BASED_UNIT('INCH',#{inch_ctx.eid})"
    f"LENGTH_UNIT()NAMED_UNIT(#{dim_exp.eid}))"
)

# ── Two shape aspects ─────────────────────────────────────────────────────────
asp_width = f._emit_raw("SHAPE_ASPECT('width_face','',#9055,.T.)")
asp_height = f._emit_raw("SHAPE_ASPECT('height_face','',#9055,.T.)")

# ── Two DIMENSIONAL_SIZEs (byte assertion: count == 2) ───────────────────────
ds_width = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp_width.eid},'width')")
ds_height = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp_height.eid},'height')")

# ── MEASURE_REPRESENTATION_ITEMs with mismatched units ───────────────────────
# 'width' in mm (SI).
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('width_nom',LENGTH_MEASURE(50.0),#9056)"
)
# 'height' in inches — mismatched unit is the defect.
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('height_nom',LENGTH_MEASURE(2.0),#{inch_unit.eid})"
)

# ── DIMENSION_PAIR coupling the two mismatched-unit dimensions ────────────────
# Defect: the two halves are in different units; receivers must normalise.
f._emit_raw(
    f"DIMENSION_PAIR('width_height_pair','mismatched units pair',"
    f"#{ds_width.eid},#{ds_height.eid})"
)
