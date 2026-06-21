"""Le008 — \\S\\ (8-bit shift) directive: misuse, chaining, or apostrophe-after-\\S\\.

Catalog claim: \\S\\x adds 0x80 to the next single ASCII character x to address
the upper half of the active ISO-8859 page. It is a one-character operator.
Defects: parser closes the string when the byte after \\S\\ is an apostrophe
('\\S\\'  — the string is seven characters, not closed early), treats the directive
as multi-character (\\S\\xy), chains it (\\S\\\\S\\E), or recurses into nested
directive parsing (\\S\\\\X\\41).

Reproducer recipe:
  'abc\\S\\'def'  (byte after \\S\\ is apostrophe — string is seven chars, not closed)
  'caf\\S\\\\S\\i' (illegal chaining of two \\S\\ directives)

Byte assertions:
  contains(b'\\\\S\\\\')
  count(b'\\\\S\\\\') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le008",
    defect=(
        "\\S\\ 8-bit shift directive misuse: apostrophe-after-\\S\\ and illegal chaining; "
        "\\S\\x adds 0x80 to the next single ASCII byte to address upper ISO-8859 page; "
        "defect 1: 'abc\\S\\'def' — apostrophe after \\S\\ is the shift operand, not string end; "
        "a parser that closes the string on the apostrophe produces a 3-char string 'abc' "
        "instead of the correct 7-char string; "
        "defect 2: 'caf\\S\\\\S\\e' — chaining two \\S\\ directives is illegal; "
        "\\S\\ is a one-character operator; spec does not permit \\S\\\\S\\ as a compound; "
        "receiver must consume exactly one byte after \\S\\ and reject or warn on chaining; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: two PERSON entities demonstrating \\S\\ misuse via render() override.
#
# PERSON #8998: apostrophe-after-\\S\\
#   The name string is 'abc\\S\\'def' which in the STEP byte stream looks like:
#     ' a b c \ S \ ' d e f '
#   The \\S\\ directive takes the next byte (' = apostrophe) as its operand,
#   making the string seven characters long. A defective parser that treats the
#   apostrophe as string terminator produces 'abc' (3 chars) and garbles 'def'.
#   Note: inside a Python string we need to double the apostrophe per STEP convention
#   so the defect byte sequence is written as \\S\\'' (the ' after \\S\\ is the operand;
#   the second ' is the STEP doubled-apostrophe that closes the field normally).
#
# PERSON #8999: chained \\S\\\\S\\e
#   Two \\S\\ directives back-to-back is not defined by the spec.
#   A conformant parser must reject or warn on the chained form.
#
# Satisfies:
#   contains(b'\\S\\')      — both entities embed \\S\\
#   count(b'\\S\\') >= 2   — #8998 has one, #8999 has two → total >= 2

_original_render = f.render


def _render_with_s_directive_defects():
    text = _original_render()
    person_lines = (
        # Apostrophe immediately after \\S\\: the ' is the shift operand, not end-of-string.
        # In the STEP literal the sequence is: ' a b c \S\ '' d e f '
        # \\S\\'' means: shift-operand=apostrophe, then STEP-doubled-apostrophe ends the field.
        "#8998=PERSON('abc\\S\\''def','apostrophe-after-S-shift','');\n"
        # Chained \\S\\ directives: \\S\\\\S\\e — two consecutive S-shift operators.
        "#8999=PERSON('caf\\S\\\\S\\e','chained-S-shift-directives','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_s_directive_defects  # type: ignore[method-assign]
