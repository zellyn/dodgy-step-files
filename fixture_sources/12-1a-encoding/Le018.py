"""Le018 — Inline newline inside a string literal silently concatenated.

Catalog claim: Per §5.2, LF and CR are ignored characters even inside
string literals, so a literal 'first line<LF>second line' parses to
'first linesecond line'.  This produces surprising silent concatenation
when round-tripping descriptions written across physical lines.

Reproducer recipe:
  FILE_DESCRIPTION(('first line<LF>second line'),'2;1');

Byte assertions:
  matches(rb"FILE_DESCRIPTION\\(\\('first line\\nsecond line'")
  matches(rb"PERSON\\(\\s*'p1','para1\\s*\\n")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le018",
    defect=(
        "Inline newline inside string literal silently concatenated; "
        "ISO 10303-21 §5.2: LF and CR are ignored (whitespace) even inside string literals; "
        "a literal newline in 'first line<LF>second line' causes the two halves to join "
        "without a separator, yielding 'first linesecond line'; "
        "producers writing multi-line descriptions across physical lines lose content; "
        "receivers must heal and accept per spec (LF is ignored, not an error); "
        "tolerant writers should pre-encode \\X\\0A when a real newline is intended; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: override render() to inject:
#   1. A FILE_DESCRIPTION header with an inline LF inside the description string.
#   2. A PERSON entity whose paragraph attribute spans a physical line break.
#
# The raw LF byte inside the string satisfies:
#   matches(rb"FILE_DESCRIPTION\(\('first line\nsecond line'")
#   matches(rb"PERSON\(\s*'p1','para1\s*\n")

_original_render = f.render


def _render_with_inline_newline() -> str:
    text = _original_render()

    # 1. Patch the FILE_DESCRIPTION line to embed a raw LF in the description string.
    # The original header looks like:
    #   FILE_DESCRIPTION(('...'),'2;1');
    # We replace it with a version that has a literal newline inside the description.
    old_fd = "FILE_DESCRIPTION(('"
    new_fd_replacement = "FILE_DESCRIPTION(('first line\nsecond line'"
    if old_fd in text:
        # Replace just the opening of the FILE_DESCRIPTION string so the rest
        # of the header line remains; find the original description content end.
        start = text.index(old_fd)
        # Find closing '),'  after the description list
        end = text.index("'),'2;1');", start)
        text = text[:start] + new_fd_replacement + text[end:]

    # 2. Inject a PERSON entity whose 'paragraph' attribute spans a physical line.
    person_line = "#8999=PERSON('p1','para1\npara2','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_inline_newline  # type: ignore[method-assign]
