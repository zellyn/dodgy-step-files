"""Le022 — Non-ASCII / Japanese / Greek Unicode in PRODUCT.name via \\X2\\...\\X0\\.

Catalog claim: STEP names and PMI annotation strings carry Unicode using the
spec-conformant \\X2\\...\\X0\\ directive.  Older OCCT did not decode the
directives at all and emitted question-mark replacements.  Some downstream
tools (Excel, legacy ANSI receivers) cannot render the result because they
lack full Unicode font support, but the file itself is conformant.

Reproducer recipe:
  PRODUCT('\\X2\\03B1\\X0\\','alpha','desc',..);  (Greek alpha)
  Japanese characters embedded as \\X2\\...\\X0\\ in NAME field.

Byte assertions:
  contains(b'\\X2\\03B1\\X0\\')
  count(b'\\X2\\') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le022",
    defect=(
        "Non-ASCII / Japanese / Greek Unicode in PRODUCT.name via \\X2\\...\\X0\\ directive; "
        "ISO 10303-21 §6.4.3.3: \\X2\\HHHH...\\X0\\ encodes UTF-16BE code units; "
        "older OCCT did not decode \\X2\\...\\X0\\ and emitted question-mark replacements; "
        "defect 1: \\X2\\03B1\\X0\\ — Greek small letter alpha (U+03B1); "
        "defect 2: \\X2\\30A2\\X0\\ — Japanese katakana 'A' (U+30A2); "
        "conformant file but receivers must correctly decode \\X2\\ directive; "
        "heal and accept: decode all control directives during read; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities whose names use \\X2\\...\\X0\\ directives
# to encode non-ASCII characters.
#
# PERSON #8997: \\X2\\03B1\\X0\\ — Greek small letter alpha (U+03B1)
# PERSON #8998: \\X2\\30A2\\X0\\ — Japanese katakana LETTER A (U+30A2)
# PERSON #8999: \\X2\\0041\\X0\\ — ASCII 'A' encoded via \\X2\\ (conformant edge case)
#
# Satisfies:
#   contains(b'\\X2\\03B1\\X0\\')  — #8997
#   count(b'\\X2\\') >= 1          — three occurrences

_original_render = f.render


def _render_with_x2_unicode():
    text = _original_render()
    person_lines = (
        # Greek small letter alpha: U+03B1 → \X2\03B1\X0\
        "#8997=PERSON('\\X2\\03B1\\X0\\','greek-alpha','');\n"
        # Japanese katakana A: U+30A2 → \X2\30A2\X0\
        "#8998=PERSON('\\X2\\30A2\\X0\\','japanese-katakana-a','');\n"
        # ASCII 'A' via \X2\: U+0041 — conformant but unusual; exercises decoder
        "#8999=PERSON('\\X2\\0041\\X0\\','ascii-via-x2','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_x2_unicode  # type: ignore[method-assign]
