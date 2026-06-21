"""Le040 — \\Q\\ numeric-character-reference at the upper Unicode boundary (U+10FFFF).

Catalog claim: Edition-3 \\Q\\NNN\\Q\\ encodes a character by its decimal
Unicode scalar value. The largest legal Unicode scalar is U+10FFFF (decimal
1114111). Many implementations accept only BMP values (up to 0xFFFF) and
silently truncate or ignore supplementary-plane scalars.

Reproducer recipe:
  PRODUCT.name='top=\\Q\\1114111\\Q\\' — payload is the decimal value of
  U+10FFFF, the topmost legal Unicode scalar.

Byte assertions:
  contains(b'\\\\Q\\\\1114111\\\\Q\\\\')
  contains(b'1114111')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le040",
    defect=(
        "\\Q\\ numeric-character-reference at the upper Unicode boundary U+10FFFF; "
        "ISO 10303-21 Ed.3 §6.4.3: \\Q\\NNN\\Q\\ encodes a Unicode scalar by decimal value; "
        "the largest legal Unicode scalar is U+10FFFF = decimal 1114111; "
        "defect string: 'top=\\Q\\1114111\\Q\\' — payload 1114111 is the decimal value "
        "of U+10FFFF, the topmost supplementary-plane scalar; "
        "implementations that only support BMP (up to 0xFFFF=65535) silently truncate "
        "or pass the digit sequence through verbatim instead of decoding the scalar; "
        "a kernel claiming Edition-3 conformance must decode 1114111 into a valid "
        "four-byte UTF-8 sequence (\\xF4\\x8F\\xBF\\xBF); "
        "ifcopenshell observed to terminate via process signal on \\Q\\..\\Q\\ payloads; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities with \\Q\\ at the U+10FFFF boundary.
#
# PERSON #8998: name = 'top=\Q\1114111\Q\'
#   Payload 1114111 is the decimal code point for U+10FFFF (LAST UNICODE CHARACTER).
#   A BMP-only decoder silently truncates this to 0xFFFF or substitutes 0.
#   A correct Ed.3 decoder maps it to the four-byte UTF-8 sequence F4 8F BF BF.
#
# PERSON #8999: name = 'hi=\Q\1114110\Q\'
#   One below the boundary (U+10FFFE) to confirm the boundary is inclusive.
#   Parsers that implement an off-by-one check (> vs >=) fail here.
#
# Satisfies:
#   contains(b'\\Q\\1114111\\Q\\')   — primary byte assertion
#   contains(b'1114111')            — secondary byte assertion

_original_render = f.render


def _render_with_q_at_unicode_ceiling() -> str:
    text = _original_render()
    person_lines = (
        # \\Q\\1114111\\Q\\: U+10FFFF — topmost legal Unicode scalar
        "#8998=PERSON('top=\\Q\\1114111\\Q\\','q-ref-at-U10FFFF','');\n"
        # \\Q\\1114110\\Q\\: U+10FFFE — one below ceiling, also supplementary-plane
        "#8999=PERSON('hi=\\Q\\1114110\\Q\\','q-ref-U10FFFE-below-ceiling','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_q_at_unicode_ceiling  # type: ignore[method-assign]
