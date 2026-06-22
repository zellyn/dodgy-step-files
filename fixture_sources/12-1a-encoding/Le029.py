"""Le029 — Header FILE_DESCRIPTION strings containing commas or parentheses.

Catalog claim: Header parsers implemented as regex-split-on-comma fail when a
description string contains literal commas or balanced parentheses. Real IFC
and STEP headers commonly carry both.

Reproducer recipe:
  FILE_DESCRIPTION(('a, b (c)','d'),'2;1');

Byte assertions:
  matches(rb"FILE_DESCRIPTION\\(\\(\\s*'[^']*\\([^)]+\\)")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le029",
    defect=(
        "Header FILE_DESCRIPTION strings containing commas or parentheses; "
        "ISO 10303-21 §8.2.1: FILE_DESCRIPTION string values are opaque; "
        "header parsers using regex-split-on-comma fail on 'a, b (c)' content; "
        "splitting on the comma inside the string yields wrong parameter count; "
        "unmatched parenthesis detection breaks on balanced parens inside strings; "
        "file uses FILE_DESCRIPTION(('a, b (c)','d'),'2;1') — comma and parens in string; "
        "correct parser must tokenise strings before splitting parameters; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: override render() to replace the auto-generated
# FILE_DESCRIPTION header line with one that embeds a comma and balanced
# parentheses inside the description string.
#
# The canonical builder emits: FILE_DESCRIPTION(('Le029'),'2;1');
# We replace it with:          FILE_DESCRIPTION(('a, b (c)','d'),'2;1');
#
# A regex-split-on-comma parser would split 'a, b (c)' at the comma,
# misreading 'a' and ' b (c)' as separate tokens, and also see the
# unbalanced open-paren in 'a' fragment. Neither split should occur.
#
# Satisfies:
#   matches(rb"FILE_DESCRIPTION\(\(\s*'[^']*\([^)]+\)")
#     — pattern matches FILE_DESCRIPTION(('a, b (c)', with open-paren inside string

_original_render = f.render


def _render_with_comma_paren_in_header() -> str:
    text = _original_render()

    # Replace the auto-generated FILE_DESCRIPTION line with the defective one.
    # The builder emits: FILE_DESCRIPTION(('Le029'),'2;1');
    old_desc = "FILE_DESCRIPTION(('Le029'),'2;1');"
    new_desc = "FILE_DESCRIPTION(('a, b (c)','d'),'2;1');"
    if old_desc not in text:
        # Fallback: replace any FILE_DESCRIPTION line
        import re
        text = re.sub(
            r"FILE_DESCRIPTION\([^;]+\);",
            new_desc,
            text,
            count=1,
        )
    else:
        text = text.replace(old_desc, new_desc, 1)

    return text


f.render = _render_with_comma_paren_in_header  # type: ignore[method-assign]
