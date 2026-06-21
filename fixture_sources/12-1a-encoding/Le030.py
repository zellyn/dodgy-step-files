"""Le030 — \\PE\\ selector and \\Q\\x directive support.

Catalog claim: ISO 10303-21 also defines \\PE\\ (UCS extended) and \\Q\\x
(alternate-quote) directives that some legacy generators emit. Few parsers
implement these, so the bytes pass through to the user as literal \\PE\\ or
\\Q\\'.

Reproducer recipe:
  '\\PE\\foo'; '\\Q\\'foo\\Q\\''

Byte assertions:
  contains(b'\\\\PE\\\\') or contains(b'\\\\Q\\\\')
  contains(b'\\\\Q\\\\') or contains(b'\\\\PE\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le030",
    defect=(
        "\\PE\\ selector and \\Q\\x alternate-quote directive support; "
        "ISO 10303-21 Ed.3 §6.4.3 defines \\PE\\ (UCS extended alphabet-extension) "
        "and \\Q\\x (alternate-quote) directives for use in string literals; "
        "legacy generators emit \\PE\\foo in PRODUCT name fields; "
        "alternate-quote directive: \\Q\\'foo\\Q\\' encodes a quoted string fragment; "
        "parsers that do not implement these directives pass bytes through verbatim "
        "producing literal \\PE\\ or \\Q\\' in the decoded attribute string; "
        "receivers must recognise and consume documented directive operands "
        "without lexer desynchronisation; warn-and-accept is the minimum requirement; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities whose name fields embed \\PE\\
# and \\Q\\x directives.
#
# PERSON #8997: '\\PE\\foo' — bare \\PE\\ with no page-selector letter consumed;
#               parsers treating \\PE\\ as unrecognised pass the 4-byte sequence
#               through literally instead of invoking the UCS-extended handler.
# PERSON #8998: '\\Q\\'foo\\Q\\'' — alternate-quote brackets; the \\Q\\' directive
#               introduces an alternate quote context; unsupporting parsers see
#               the apostrophe inside \\Q\\' as the string terminator.
#
# Satisfies:
#   contains(b'\\PE\\')  — #8997
#   contains(b'\\Q\\')   — #8998

_original_render = f.render


def _render_with_pe_q_directives() -> str:
    text = _original_render()
    person_lines = (
        # \\PE\\ with no page-selector: legacy generators may emit bare \\PE\\
        "#8997=PERSON('\\PE\\foo','pe-directive-no-selector','');\n"
        # \\Q\\x alternate-quote: \\Q\\' starts alternate-quote context
        "#8998=PERSON('\\Q\\'foo\\Q\\'','q-alternate-quote','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_pe_q_directives  # type: ignore[method-assign]
