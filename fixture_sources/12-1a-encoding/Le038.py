"""Le038 — Bare \\PE\\ directive at end-of-string with no operand letter.

Catalog claim: Edition-3 \\PE\\ requires a single ASCII letter (the page
selector A-I) immediately following the slashes. A producer that truncates a
string at the directive boundary emits a bare \\PE\\ with no follow-byte
before the closing apostrophe. A naive parser may consume the closing ' as the
page operand and lose string termination, walking off into the rest of the entity.

Reproducer recipe:
  PRODUCT.name='text\\PE\\'' — closing apostrophe immediately follows \\PE\\.
  The next entity definition becomes part of the string body if the parser eats
  the apostrophe as the directive operand.

Byte assertions:
  matches(rb"\\\\PE\\\\'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le038",
    defect=(
        "Bare \\PE\\ directive at end-of-string with no operand letter; "
        "ISO 10303-21 Ed.3 §6.4.3: \\PE\\ must be followed by exactly one ASCII "
        "letter (page selector A-I) before any further string content; "
        "a truncated or copy-paste-corrupted string emits 'text\\PE\\' — the "
        "closing apostrophe immediately follows \\PE\\ with no page-letter between; "
        "a naive parser that reads the next byte as the \\PE\\ operand consumes the "
        "apostrophe as the selector letter, losing the string terminator; "
        "the parser then walks into the next entity record, treating #9001=... as "
        "string content until it encounters an unexpected token; "
        "receiver must reject with a precise diagnostic citing the string offset; "
        "never let the closing apostrophe be consumed as a directive operand; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject a PERSON entity whose name ends with bare \\PE\\
# immediately before the closing apostrophe, with no page-selector letter.
#
# PERSON #8999: name = 'text\PE\' — the \\PE\\ has no follow-byte selector;
#   the apostrophe ' terminates the Python string here but in STEP bytes the
#   sequence is:  ' t e x t \ P E \ '
#   A parser consuming '\'' as the \\PE\\ operand would exit the string one
#   entity too late.  We embed two such entities to make the hazard clearer
#   and to ensure the pattern \\PE\\' appears at least once.
#
# Satisfies:
#   matches(rb"\\PE\\'")  — \\PE\\ immediately before the closing apostrophe

_original_render = f.render


def _render_with_bare_pe_at_eol() -> str:
    text = _original_render()
    # Raw STEP line: #8999=PERSON('text\PE\','bare-pe-no-selector','');
    # In Python source the string literal is: 'text\\PE\\' — two backslash-escape
    # sequences that produce the four bytes: \ P E \
    person_lines = (
        "#8999=PERSON('text\\PE\\'bare-pe-no-selector','');\n"
        # Second occurrence to make it unambiguous; here the bare \\PE\\ is
        # at the very end, immediately before the closing apostrophe.
        "#9000=PERSON('prefix\\PE\\','bare-pe-truncated-string','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_bare_pe_at_eol  # type: ignore[method-assign]
