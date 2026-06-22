"""Le017 — Raw control character (U+0000..U+001F) in string body.

Catalog claim: Control characters (tab, LF, CR, NUL, etc.) must be encoded
as \\X\\hh (e.g. tab = \\X\\09); raw bytes in a string literal are illegal
even under the Ed.3 UTF-8 default.  Files written by tools using "binary
write" of attribute strings often contain raw \\t, \\n, or \\0.  Some
parsers tolerate raw \\n and then index past the line buffer when computing
line/column for diagnostics.

Reproducer recipe:
  'first line<RAW LF>second'
  #1=PERSON('line1<RAW LF>line2');

Byte assertions:
  matches(rb"'[^']*[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f][^']*'")
  matches(rb"'[^']*\\t[^']*'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le017",
    defect=(
        "Raw control character (U+0000..U+001F) inside string body; "
        "ISO 10303-21 §6.4.3.4: control chars must be encoded as \\X\\HH; "
        "raw bytes including tab (\\x09), vertical-tab (\\x0B), form-feed (\\x0C), "
        "and other C0 control bytes are spec-illegal in string literals; "
        "tools using binary-write mode copy raw control bytes into attribute strings; "
        "parsers tolerating raw \\n may index past the line buffer computing line/col; "
        "receiver must reject or warn; must not silently produce wrong attribute value; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: PERSON entities whose name strings contain raw control bytes.
#
# PERSON #8997: raw TAB (0x09) inside a string literal
# PERSON #8998: raw vertical-tab (0x0B) inside a string literal
#
# Byte assertions are satisfied directly by the injected bytes:
#   matches(rb"'[^']*[\x00-\x08\x0b\x0c\x0e-\x1f][^']*'")  — \x0b in #8998
#   matches(rb"'[^']*\t[^']*'")                               — \x09 (TAB) in #8997

_original_render = f.render


def _render_with_raw_control_chars() -> str:
    text = _original_render()
    # Build the injected bytes explicitly so Python escape sequences
    # produce the raw control-byte values in the output string.
    tab = "\x09"       # U+0009 HORIZONTAL TAB — raw, spec-illegal in string literal
    vtab = "\x0B"      # U+000B VERTICAL TAB — raw, spec-illegal in string literal
    person_lines = (
        f"#8997=PERSON('line1{tab}line2','raw-tab-in-string','');\n"
        f"#8998=PERSON('line1{vtab}line2','raw-vtab-in-string','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_raw_control_chars  # type: ignore[method-assign]
