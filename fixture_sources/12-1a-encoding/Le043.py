"""Le043 — \\X4\\ with a valid supplementary-plane code point followed by a short trailing hex run.

Catalog claim: ISO 10303-21 Ed.3 §6.4.3 \\X4\\...\\X0\\ wraps a sequence of
8-hex-digit groups, each encoding one UCS-4 (32-bit) scalar. A producer
concatenating variable-length output may emit a hex run not divisible by 8.
Distinct from Le006 in that the *valid* leading group is a supplementary-plane
scalar (U+1F600 Grinning Face) and only the trailing group is short, so a
tolerant parser may accept the first character and silently drop the second.

Reproducer recipe:
  PRODUCT.name='mix=\\X4\\0001F60000041\\X0\\' — 8 hex digits (U+1F600, valid SMP)
  followed by 4 hex digits (short, illegal).

Byte assertions:
  contains(b'\\\\X4\\\\0001F60000041\\\\X0\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le043",
    defect=(
        "\\X4\\ with a valid supplementary-plane code point followed by a short trailing hex run; "
        "ISO 10303-21 Ed.3 §6.4.3: \\X4\\HHHHHHHH...\\X0\\ requires exactly 8 hex digits "
        "per 32-bit UCS-4 code point; a total hex run not divisible by 8 is malformed; "
        "defect string: 'mix=\\X4\\0001F60000041\\X0\\' — the 12-digit hex run contains "
        "a valid 8-digit group (0001F600 = U+1F600, Grinning Face emoji) immediately followed "
        "by a short 4-digit group (0041 = 'A') that does not form a full 8-digit UCS-4 unit; "
        "distinct from Le006: Le043 has a valid leading group so a tolerant parser may decode "
        "the first character and silently drop the second, hiding the malformation; "
        "receiver must reject the whole \\X4\\...\\X0\\ block as malformed, "
        "or reject only the trailing short group with a diagnostic; "
        "never silently truncate the trailing hex digits; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities with mixed-validity \\X4\\ hex runs.
#
# PERSON #8998: name = 'mix=\X4\0001F60000041\X0\'
#   12 hex digits total: 0001F600 (U+1F600, valid SMP) + 0041 (short, 4 digits only).
#   A 12-digit run is not divisible by 8, making the whole block malformed.
#   Tolerant parsers may decode U+1F600 and silently drop '0041'.
#
# PERSON #8999: name = 'grin=\X4\0001F6000001F601\X0\'
#   16 hex digits: two valid 8-digit groups (U+1F600, U+1F601).
#   Control case: a correctly divisible-by-8 run that parsers should accept.
#   Included to confirm the parser can handle \\X4\\ at all, and to provide
#   contrast showing the 12-digit case is distinctly wrong.
#
# Satisfies:
#   contains(b'\\X4\\0001F60000041\\X0\\')  — primary byte assertion

_original_render = f.render


def _render_with_x4_mixed_valid_short() -> str:
    text = _original_render()
    person_lines = (
        # 12-digit run: valid 8-digit U+1F600 + short 4-digit 0041 (malformed)
        "#8998=PERSON('mix=\\X4\\0001F60000041\\X0\\','x4-valid-smp-plus-short-tail','');\n"
        # 16-digit run: two valid 8-digit groups as a non-defect control
        "#8999=PERSON('grin=\\X4\\0001F6000001F601\\X0\\','x4-two-valid-smp-groups','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_x4_mixed_valid_short  # type: ignore[method-assign]
