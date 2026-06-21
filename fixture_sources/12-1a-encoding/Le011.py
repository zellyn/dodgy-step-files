"""Le011 — \\N\\ notation directive misused as C-style newline escape.

Catalog claim: \\N\\ toggles a notation context. Generators emit it without the
spec-required following digit, or assume it means "newline" (it does not; newlines
must be encoded as \\X\\0A). The same defect can also span a physical line break
in the source.

Reproducer recipe:
  'line1\\N\\line2'  (writer assumed \\N\\ == LF — it does not)

Byte assertions:
  contains(b'\\\\N\\\\')
  count(b'\\\\N\\\\') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le011",
    defect=(
        "\\N\\ notation directive misused as C-style newline escape; "
        "\\N\\ toggles a notation context per ISO 10303-21 §6.4.3 Table 4; "
        "it is NOT a newline — a literal newline must be encoded as \\X\\0A; "
        "defect: 'line1\\N\\line2' — the producer confused \\N\\ with C '\\n'; "
        "a tolerant reader must not crash; it should warn that \\N\\ is not a newline; "
        "literal text intended by the producer is silently re-flowed and the loaded "
        "attribute differs from the source bytes; "
        "multiple \\N\\ occurrences demonstrate the repeated-misuse pattern; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: two PERSON entities where \\N\\ is misused as a newline escape
# via render() override.
#
# PERSON #8998: 'line1\\N\\line2' — \\N\\ used as if it were a C-style \\n.
# PERSON #8999: 'para1\\N\\para2\\N\\para3' — repeated misuse across a multi-paragraph
#   description; three \\N\\ in a single string, two of which appear here.
#
# Satisfies:
#   contains(b'\\N\\')      — both entities embed \\N\\
#   count(b'\\N\\') >= 2   — #8998 has one, #8999 has two → total >= 3

_original_render = f.render


def _render_with_n_directive_misuse():
    text = _original_render()
    person_lines = (
        # Single \\N\\ misused as newline between 'line1' and 'line2'
        "#8998=PERSON('line1\\N\\line2','N-directive-as-newline','');\n"
        # Repeated \\N\\ misuse: three "newlines" in a description field
        "#8999=PERSON('para1\\N\\para2\\N\\para3','repeated-N-directive-newline','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_n_directive_misuse  # type: ignore[method-assign]
