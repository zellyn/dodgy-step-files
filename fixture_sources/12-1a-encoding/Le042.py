"""Le042 — \\Q\\ payload contains non-decimal characters.

Catalog claim: ISO 10303-21 Ed.3 §6.4.3 requires the \\Q\\NNN\\Q\\ bracketed
payload to be a decimal integer. Producers occasionally emit hex digits
('\\Q\\1F600\\Q\\'), an '0x' prefix ('\\Q\\0x41\\Q\\'), or whitespace
('\\Q\\ 65 \\Q\\'). A strict parser rejects; a lenient parser may silently
coerce via leading digits, producing the wrong character.

Reproducer recipe:
  'hex=\\Q\\F60\\Q\\'; 'px=\\Q\\0x41\\Q\\'; 'ws=\\Q\\ 65 \\Q\\'

Byte assertions:
  contains(b'\\\\Q\\\\0x') or matches(rb'\\\\Q\\\\\\\\s')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le042",
    defect=(
        "\\Q\\ payload contains non-decimal characters; "
        "ISO 10303-21 Ed.3 §6.4.3: \\Q\\NNN\\Q\\ payload must be a decimal integer; "
        "producers emit hex digits '\\Q\\1F600\\Q\\', an '0x' prefix '\\Q\\0x41\\Q\\', "
        "or whitespace '\\Q\\ 65 \\Q\\' around the number; "
        "a strict parser must reject with a precise diagnostic citing the offending characters; "
        "a lenient parser that extracts leading decimal digits from '\\Q\\0x41\\Q\\' produces "
        "decimal 0 instead of 65 (0x41 = 'A'), silently substituting the wrong character; "
        "similarly '\\Q\\F60\\Q\\' with no leading decimal digit may be coerced to 0 or garbage; "
        "never silently substitute 0 for a malformed payload; "
        "ifcopenshell observed to terminate via process signal on \\Q\\..\\Q\\ payloads; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities with malformed \\Q\\ payloads.
#
# PERSON #8997: name = 'hex=\Q\F60\Q\'
#   Payload 'F60' — starts with 'F', a hex digit but not decimal.
#   A strict parser rejects; a lenient one parses leading digits = 0.
#
# PERSON #8998: name = 'px=\Q\0x41\Q\'
#   Payload '0x41' — C-style hex prefix; decimal parser should reject.
#   A lenient parser extracts leading '0' = code point 0 (NUL) instead of 65.
#
# PERSON #8999: name = 'ws=\Q\ 65 \Q\'
#   Payload ' 65 ' with leading and trailing whitespace.
#   Some parsers skip whitespace (producing correct 65); strict parsers reject.
#
# Satisfies:
#   contains(b'\\Q\\0x')  — primary byte assertion (0x prefix form)

_original_render = f.render


def _render_with_q_nondecimal_payloads() -> str:
    text = _original_render()
    person_lines = (
        # Pure hex digits (no 0x prefix): 'F60' starts with non-decimal 'F'
        "#8997=PERSON('hex=\\Q\\F60\\Q\\','q-payload-hex-digits','');\n"
        # '0x' prefix: C-style hex notation in decimal-only context
        "#8998=PERSON('px=\\Q\\0x41\\Q\\','q-payload-0x-prefix','');\n"
        # Whitespace padding: ' 65 ' has leading/trailing spaces
        "#8999=PERSON('ws=\\Q\\ 65 \\Q\\','q-payload-whitespace','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_q_nondecimal_payloads  # type: ignore[method-assign]
