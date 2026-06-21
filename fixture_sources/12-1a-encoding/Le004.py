"""Le004 — \\X\\ (single-byte ISO-8859) escape with bad hex digit count or non-hex input.

Catalog claim: \\X\\HH must consume exactly two upper-case hex digits to encode
an 8-bit ISO-8859-* code point. Real files emit one digit (\\X\\F), three or
more (\\X\\FFA), lowercase (\\X\\e9), non-hex (\\X\\GG), or interpose whitespace
(\\X\\E9 9). A loose parser may walk past the directive boundary or accept
malformed values.

Reproducer recipe: 'caf\\X\\e9', 'caf\\X\\009', 'caf\\X\\F', 'caf\\X\\E9 9'

Byte assertions:
  contains(b'\\X\\e9')
  contains(b'\\X\\009')
  contains(b'\\X\\F')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le004",
    defect=(
        "\\X\\ single-byte ISO-8859 escape with bad hex digit count or non-hex input; "
        "\\X\\HH must consume exactly two upper-case hex digits; "
        "defects: one digit (\\X\\F), three digits (\\X\\009), lowercase (\\X\\e9), "
        "non-hex (\\X\\GG), or whitespace interposed (\\X\\E9 9); "
        "strict parser emits E_BAD_X_DIRECTIVE; tolerant reader may accept lowercase "
        "by case-folding but must reject odd or non-hex digit counts; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities using malformed \\X\\ escapes via
# render() override. Each PERSON name exercises a different malformation:
#   - 'caf\\X\\e9'   — lowercase hex (should be \\X\\E9)
#   - 'caf\\X\\009'  — three hex digits instead of two
#   - 'caf\\X\\F'    — single hex digit (truncated)
#
# Satisfies:
#   contains(b'\\X\\e9')
#   contains(b'\\X\\009')
#   contains(b'\\X\\F')

_original_render = f.render


def _render_with_bad_x_escape():
    text = _original_render()
    # Three PERSON entities, each with a different \\X\\ malformation.
    person_lines = (
        # Lowercase hex: spec requires upper-case A-F; \\X\\e9 is non-conformant
        "#8997=PERSON('caf\\X\\e9','lowercase-hex-x-escape','');\n"
        # Three hex digits: \\X\\ takes exactly two; \\X\\009 has an extra digit
        "#8998=PERSON('caf\\X\\009','three-digit-x-escape','');\n"
        # Single hex digit: \\X\\ must have exactly two; \\X\\F is truncated
        "#8999=PERSON('caf\\X\\F','single-digit-x-escape','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_bad_x_escape  # type: ignore[method-assign]
