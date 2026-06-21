"""Le027 — 8-bit characters and case-insensitive keyword tolerance in lexer.

Catalog claim: OCCT's lex grammar explicitly tolerates 8-bit characters and
case-insensitive keywords. A schema-loader that rewrites every byte >= 0x80
to space and reports an error rejects EXPRESS schemas with Latin-1 in
comments (e.g. °C). Mixed-case keywords like 'iso-10303-21;' exercise
case-insensitive parsing.

Reproducer recipe:
  STEP file header keyword: iso-10303-21; (lowercase instead of ISO-10303-21;)
  An entity name or description containing bytes >= 0x80 (Latin-1 encoded °).

Byte assertions:
  contains(b'iso-10303-21;') or contains(b'EndSec;') or contains(b'End-Iso-10303-21;')
  matches(rb'[\\x80-\\xff]')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=reject
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le027",
    defect=(
        "8-bit characters and case-insensitive keyword tolerance in lexer; "
        "ISO 10303-21 §6.1: magic line is 'ISO-10303-21;' in uppercase; "
        "OCCT lex grammar (StepFile/step.lex:30-35) tolerates lowercase 'iso-10303-21;'; "
        "schema-loaders that rewrite bytes >= 0x80 to space reject Latin-1 in comments; "
        "file uses mixed-case keyword: 'iso-10303-21;' (all lowercase) as magic line; "
        "Latin-1 high-bit byte (0xB0 = degree sign) injected into a PERSON name field; "
        "pure-Python Part-21 validator rejects with E_MAGIC_CASE; OCCT silently heals; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: override render() to:
#   1. Replace the 'ISO-10303-21;' magic line with lowercase 'iso-10303-21;'
#      and 'END-ISO-10303-21;' with 'End-Iso-10303-21;'.
#   2. Inject a PERSON entity whose name contains a raw Latin-1 byte >= 0x80
#      (0xB0 = degree sign °).
#
# Satisfies:
#   contains(b'iso-10303-21;')        — magic line lowercased
#   contains(b'End-Iso-10303-21;')    — end marker mixed-case
#   matches(rb'[\x80-\xff]')          — raw 0xB0 in PERSON name

_original_render = f.render


def _render_with_mixed_case_and_highbyte() -> str:
    text = _original_render()

    # Step 1: replace magic bookends with mixed-case equivalents
    text = text.replace("ISO-10303-21;\n", "iso-10303-21;\n", 1)
    text = text.replace("\nEND-ISO-10303-21;\n", "\nEnd-Iso-10303-21;\n", 1)

    # Step 2: inject PERSON entity with raw high-byte sequences in the name.
    # The degree symbol as raw UTF-8 multibyte bytes (U+00B0 = 0xC2 0xB0) is
    # legal UTF-8 but illegal in Ed.2 STEP (which requires \X\B0 escaping).
    # Schema-loaders that strip or replace bytes >= 0x80 will mangle this name.
    # Using UTF-8 here keeps the Python source and .stp file valid UTF-8 so
    # write_text() / read_text() roundtrip cleanly.
    degree_sign = "°"  # U+00B0 DEGREE SIGN; UTF-8: 0xC2 0xB0
    person_line = f"#8997=PERSON('{degree_sign}C','raw-utf8-degree-celsius','');\n"

    marker = "\nENDSEC;\nEnd-Iso-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_mixed_case_and_highbyte  # type: ignore[method-assign]
