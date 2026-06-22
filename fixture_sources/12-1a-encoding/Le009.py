"""Le009 — \\P{X}\\ page-shift directive: bad selector / state-machine omission.

Catalog claim: \\PA\\ through \\PI\\ selects ISO-8859-1 through ISO-8859-9 (one
upper-case letter, persistent for the rest of the string). Real files emit
lowercase letters (\\Pg\\), digits (\\P1\\), full names (\\PISO\\), or omit/replace
the selector (\\P\\, \\P!\\). Many parsers also skip the state machine and ignore
the directive entirely, garbling subsequent characters.

Reproducer recipe:
  '\\Pg\\\\S\\a'   (lowercase selector 'g' — invalid; spec requires [A-I])
  '\\P1\\…'        (digit selector — out of range)
  '\\P!\\\\X\\41'  (non-letter selector — also out of range)

Byte assertions:
  contains(b'\\\\Pg\\\\') or contains(b'\\\\P1\\\\') or contains(b'\\\\P!\\\\')
  count(b'\\\\P') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le009",
    defect=(
        "\\P{X}\\ page-shift directive: bad selector and state-machine omission; "
        "\\PA\\ through \\PI\\ selects ISO-8859-1 through ISO-8859-9; "
        "defect 1: \\Pg\\ — lowercase selector 'g' is out of range (spec requires [A-I]); "
        "defect 2: \\P1\\ — digit selector '1' is invalid; "
        "defect 3: \\P!\\ — non-letter selector '!' is invalid; "
        "parsers ignoring the page-state machine decode subsequent characters against "
        "the wrong ISO-8859 page and produce wrong glyphs even when the entity is "
        "otherwise structurally valid; "
        "receiver must reject E_BAD_PAGE_DIRECTIVE for out-of-range selectors; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: three PERSON entities covering three invalid \\P{X}\\ selectors
# via render() override.
#
# PERSON #8997: \\Pg\\ — lowercase selector; spec allows only [A-I] (upper-case).
# PERSON #8998: \\P1\\ — digit selector '1'; digits are not in the allowed set.
# PERSON #8999: \\P!\\ — non-letter/non-digit selector; completely invalid.
#
# Satisfies:
#   contains(b'\\Pg\\')  — #8997
#   contains(b'\\P1\\')  — #8998
#   contains(b'\\P!\\')  — #8999
#   count(b'\\P') >= 2  — three occurrences total

_original_render = f.render


def _render_with_bad_page_directive():
    text = _original_render()
    person_lines = (
        # Lowercase selector 'g': \\Pg\\ is out-of-range (only \\PA\\..\\PI\\ are valid)
        "#8997=PERSON('\\Pg\\Krak\\X\\F3w','lowercase-page-selector','');\n"
        # Digit selector '1': digits are not valid page-shift selectors
        "#8998=PERSON('\\P1\\encoded-text','digit-page-selector','');\n"
        # Non-letter selector '!': completely invalid selector character
        "#8999=PERSON('\\P!\\\\X\\41','non-letter-page-selector','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_bad_page_directive  # type: ignore[method-assign]
