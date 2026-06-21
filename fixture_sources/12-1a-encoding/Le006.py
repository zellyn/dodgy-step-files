"""Le006 — \\X4\\…\\X0\\ (UCS-4) escape with hex run not divisible by 8 or containing surrogate code points.

Catalog claim: \\X4\\ requires hex digit count divisible by eight (one 32-bit
code point per group). Tools emit 4-digit or 6-digit groups, embed UTF-16
surrogate halves directly (illegal as UCS-4 code points), or omit \\X0\\.

Reproducer recipe:
  'pi=\\X4\\03C0\\X0\\' (only 4 digits — should be 8)
  'oops=\\X4\\0000D83D\\X0\\' (lone surrogate U+D83D)
  '\\X4\\00110000\\X0\\' (above U+10FFFF)

Byte assertions:
  contains(b'\\X4\\03C0\\X0\\')
  contains(b'\\X4\\0000D83D\\X0\\')
  contains(b'\\X4\\00110000\\X0\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le006",
    defect=(
        "\\X4\\ UCS-4 escape with hex run not divisible by 8 or containing illegal code points; "
        "\\X4\\HHHHHHHH…\\X0\\ requires 8 hex digits per 32-bit code point; "
        "defects: 4-digit group \\X4\\03C0\\X0\\ (pi symbol truncated), "
        "lone surrogate \\X4\\0000D83D\\X0\\ (U+D83D — illegal in UCS-4), "
        "above U+10FFFF: \\X4\\00110000\\X0\\ (U+110000 out-of-range); "
        "receiver must reject; tolerant readers must flag surrogates (U+D800..U+DFFF) "
        "and values above U+10FFFF as malformed; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: three PERSON entities covering three distinct \\X4\\ defect
# classes via render() override:
#   1. 4-digit group: \\X4\\03C0\\X0\\ — pi (U+03C0) but only 4 hex digits, not 8
#   2. Lone surrogate: \\X4\\0000D83D\\X0\\ — U+D83D is a UTF-16 high surrogate
#      which is illegal as a UCS-4 code point
#   3. Above U+10FFFF: \\X4\\00110000\\X0\\ — U+110000 exceeds maximum Unicode
#
# Satisfies:
#   contains(b'\\X4\\03C0\\X0\\')
#   contains(b'\\X4\\0000D83D\\X0\\')
#   contains(b'\\X4\\00110000\\X0\\')

_original_render = f.render


def _render_with_bad_x4_escapes():
    text = _original_render()
    person_lines = (
        # 4-digit group: spec requires 8 digits; \\X4\\03C0 is truncated (pi = U+03C0)
        "#8997=PERSON('pi=\\X4\\03C0\\X0\\','four-digit-ucs4-group','');\n"
        # Lone surrogate: U+D83D is a UTF-16 high surrogate; illegal as UCS-4 codepoint
        "#8998=PERSON('oops=\\X4\\0000D83D\\X0\\','lone-surrogate-in-ucs4','');\n"
        # Above U+10FFFF: U+110000 is one beyond the maximum Unicode code point
        "#8999=PERSON('\\X4\\00110000\\X0\\','above-unicode-maximum','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_bad_x4_escapes  # type: ignore[method-assign]
