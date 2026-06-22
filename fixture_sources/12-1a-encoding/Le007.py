"""Le007 — \\X2\\ endianness confusion / lone-surrogate handling.

Catalog claim: \\X2\\ 4-digit groups are big-endian by spec; parsers built on
little-endian assumptions may interpret them backwards, producing wrong code
points and possibly invalid surrogate pairs. A downstream UTF-8 encoder fed a
lone or invalid surrogate then emits invalid UTF-8 that subsequent consumers
reject (potentially via SIGABRT).

Reproducer recipe: '\\X2\\D800\\X0\\' (lone high surrogate).

Byte assertions:
  contains(b'\\X2\\D800\\X0\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le007",
    defect=(
        "\\X2\\ UCS-2 endianness confusion and lone-surrogate handling; "
        "\\X2\\ 4-digit groups are big-endian by spec; "
        "\\X2\\D800\\X0\\ encodes lone high surrogate U+D800 — illegal in UCS-2; "
        "parsers with little-endian assumption interpret 0xD800 as 0x00D8 producing "
        "wrong code points; downstream UTF-8 encoder fed lone surrogate emits invalid UTF-8; "
        "subsequent consumers reject invalid UTF-8 or abort (SIGABRT); "
        "receiver must validate surrogate pairing; reject lone surrogates; "
        "always interpret hex groups as big-endian; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject a PERSON entity with lone high surrogate \\X2\\D800\\X0\\
# via render() override. U+D800 is the first UTF-16 high surrogate code unit;
# it is never valid as a standalone UCS-2 code point and must never appear alone
# in a \\X2\\ escape (only a matched high+low surrogate pair U+D800..U+DBFF /
# U+DC00..U+DFFF would form a valid supplementary character, and that is
# expressed differently in Part-21 via \\X4\\).
#
# Satisfies: contains(b'\\X2\\D800\\X0\\')

_original_render = f.render


def _render_with_lone_surrogate():
    text = _original_render()
    # PERSON with lone high surrogate \\X2\\D800\\X0\\:
    # U+D800 is the first UTF-16 high surrogate — illegal as standalone UCS-2 codepoint.
    # A little-endian parser would flip bytes and read U+00D8 (capital O-stroke Ø) —
    # wrong code point, demonstrating the endianness confusion.
    # A strict parser must reject: lone surrogates are never valid Unicode scalar values.
    person_line = "#8999=PERSON('\\X2\\D800\\X0\\','lone-high-surrogate-ucs2','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_lone_surrogate  # type: ignore[method-assign]
