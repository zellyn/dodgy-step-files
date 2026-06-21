"""M006 — integer_representation_item serialized without trailing decimal point.

Catalog claim: integer_representation_item.the_value is logically INTEGER but
Part 21 emits it as REAL because the attribute was redeclared from NUMBER. Files
where it appears without a trailing dot are non-conforming, and many writers do
exactly that. Strict-parse-as-REAL fails; falling back to INTEGER works but
cannot validate.

Reproducer recipe: Write INTEGER_REPRESENTATION_ITEM('number of children', 4)
(no decimal). Compare with conformant INTEGER_REPRESENTATION_ITEM('number of
children', 4.).

Byte assertions:
  contains(b'INTEGER_REPRESENTATION_ITEM')
  matches(rb"INTEGER_REPRESENTATION_ITEM\('number of faces',6\)")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M006",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing INTEGER_REPRESENTATION_ITEM without trailing "
        "decimal point; "
        "integer_representation_item.the_value redeclared from NUMBER to INTEGER in schema; "
        "non-conforming writers emit INTEGER without trailing dot (e.g., 4 instead of 4.); "
        "strict-parse-as-REAL fails on integers without dot; "
        "INTEGER_REPRESENTATION_ITEM('number of faces',6) — no trailing decimal on 6; "
        "kernel must heal and accept both forms on import; "
        "write trailing-dot form on export; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: integer_representation_item missing dot, INTEGER serialized as REAL, "
        "Part-21 INTEGER without trailing decimal, non-conforming integer encoding"
    ),
)

# ── Six dummy CARTESIAN_POINTs — one per 'face' counted by the integer property ──
# The property claims 6 faces; emit 6 points to give the count physical grounding.
pts = [f.cartesian_point((float(i), 0.0, 0.0)) for i in range(6)]

# ── The defect: INTEGER_REPRESENTATION_ITEM with no trailing dot on the integer ──
# Conformant form: INTEGER_REPRESENTATION_ITEM('number of faces',6.)
# Defective form:  INTEGER_REPRESENTATION_ITEM('number of faces',6)   <- no dot
# Byte assertion: matches(rb"INTEGER_REPRESENTATION_ITEM\('number of faces',6\)")
int_item = f._emit_raw("INTEGER_REPRESENTATION_ITEM('number of faces',6)")

# A second one for 'number of children' to match the catalog description as well
int_item2 = f._emit_raw("INTEGER_REPRESENTATION_ITEM('number of children',4)")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('integer-repr-item-missing-dot',"
    f"({','.join('#' + str(p.eid) for p in pts)},"
    f"#{int_item.eid},#{int_item2.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M006.stp")
