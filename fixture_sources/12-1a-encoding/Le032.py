"""Le032 — \\X2\\…\\X0\\ escape spanning a physical line break.

Catalog claim: A pretty-printer or broken splice writes a hex run across a
\\r\\n boundary, e.g. \\X2\\30A2 30A4\\X0\\ where the space is actually a CR LF.
Per Part-21 §5.2 those bytes are ignored, so a tolerant lexer must accept the
split; but many implementations consume the directive byte-greedily and fail
on the line-end.

Reproducer recipe:
  a STRING literal 'foo\\X2\\30A2<CR LF>30A4\\X0\\bar' split mid-escape.

Byte assertions:
  matches(rb'\\\\X2\\\\[^\\\\\\\\]*\\r?\\n[^\\\\\\\\]*\\\\X0\\\\')
  count(b'\\\\X2\\\\') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le032",
    defect=(
        "\\X2\\…\\X0\\ escape spanning a physical CR LF line break; "
        "ISO 10303-21 §5.2: whitespace (including CR LF) within a string literal "
        "is ignored by the lexer, permitting a hex run to span a line boundary; "
        "broken pretty-printers or line-length limiters split \\X2\\30A2 30A4\\X0\\ "
        "with an actual CR LF between the two 4-digit groups; "
        "byte-greedy implementations consume the directive byte-by-byte and fail "
        "when they encounter CR (0x0D) inside the hex run; "
        "tolerant lexer must skip embedded whitespace inside \\X2\\ hex runs; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: override render() to inject a PERSON entity whose name
# contains an \\X2\\...\\X0\\ run split by a CR LF line break mid-hex.
#
# The raw bytes emitted are:
#   'foo\X2\30A2\r\n30A4\X0\bar'
#
# The CR LF between the two 4-digit UCS-2 groups (U+30A2 and U+30A4) is
# legal per §5.2 (whitespace inside string literals is ignored) but breaks
# byte-greedy directive parsers that do not skip embedded line endings.
#
# Satisfies:
#   matches(rb'\\X2\\[^\\\\]*\r?\n[^\\\\]*\\X0\\')  — CRLF inside \\X2\\ run
#   count(b'\\X2\\') >= 1

_original_render = f.render


def _render_with_x2_spanning_crlf() -> str:
    text = _original_render()
    # Build the PERSON line with a CR LF embedded inside the \X2\ hex run.
    # Python string: 'foo\X2\30A2\r\n30A4\X0\bar'
    # In the STEP file this becomes:
    #   #8999=PERSON('foo\X2\30A2<CR><LF>30A4\X0\bar','x2-split-crlf','');
    person_line = (
        "#8999=PERSON('foo\\X2\\30A2\r\n"
        "30A4\\X0\\bar','x2-split-crlf','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_x2_spanning_crlf  # type: ignore[method-assign]
