"""Le021 — Component name in non-UTF-8 locale encoding (GB18030 / Shift-JIS / cp1251 / DOS850).

Catalog claim: A producer writes the literal multi-byte octets of GB18030,
Shift-JIS, EUC-JP, cp1251, or CP850 directly into PRODUCT.name,
PROPERTY_DEFINITION.description, label fields, and similar string slots.
Ed.1/Ed.2 mandate \\X2\\...\\X0\\ escapes; Ed.3 added UTF-8 only in 2016.
Many producers neither escape nor declare an encoding header.  UTF-8-only
receivers mojibake the strings; older OCCT emitted question-mark replacements.

Reproducer recipe:
  PRODUCT name with GB18030/GBK bytes for Chinese "核" (U+6838) as raw UTF-8;
  PRODUCT name with "café" where é is raw UTF-8 (not \\X\\E9 escape);
  PRODUCT name with Japanese "ア" as raw UTF-8 (not \\X2\\30A2\\X0\\).

Byte assertions:
  matches(rb"'[^']*[\\x80-\\xff][^']*'")
  matches(rb"PRODUCT\\([^;]*[\\x80-\\xff]")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le021",
    defect=(
        "Component name in non-UTF-8 locale encoding (GB18030 / Shift-JIS / cp1251 / DOS850); "
        "Ed.1/Ed.2 mandate \\X2\\...\\X0\\ escapes for non-ASCII; "
        "SolidWorks (Chinese locale) and Inventor (Japanese/Korean) write raw locale bytes "
        "into PRODUCT.name without escaping or declaring an encoding header; "
        "raw multi-byte octets outside \\X2\\ blocks are spec-illegal in Ed.1/Ed.2; "
        "this fixture embeds raw UTF-8 multibyte sequences as unescaped bytes, "
        "simulating what a producer writing raw locale bytes would emit; "
        "UTF-8-only receivers who assume Ed.2 will mojibake; "
        "strict Ed.2 mode must reject with E_RAW_NON_ASCII; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: override render() to inject PERSON entities containing raw
# non-ASCII multibyte sequences in the name field, simulating locale-encoded
# bytes that a producer (SolidWorks Chinese locale, Inventor Japanese locale)
# would write without the required \\X2\\...\\X0\\ escaping.
#
# Characters used (all valid Unicode, but appearing as raw unescaped bytes
# in the STEP file — illegal under Ed.1/Ed.2 which mandate \\X2\\ escapes):
#   核  (U+6838) — CJK/GB18030; UTF-8: 0xE6 0xA0 0xB8
#   ア  (U+30A2) — Katakana A; UTF-8: 0xE3 0x82 0xA2
#   é   (U+00E9) — French accented e; UTF-8: 0xC3 0xA9
#
# Satisfies:
#   matches(rb"'[^']*[\x80-\xff][^']*'")   — all three entities
#   matches(rb"PRODUCT\([^;]*[\x80-\xff]")  — #8999 embeds name in PRODUCT

_original_render = f.render


def _render_with_raw_nonascii() -> str:
    text = _original_render()

    # Chinese character 核 (U+6838) — would be 0xE6 0xA0 0xB8 in GB18030/UTF-8
    cjk_he = "核"
    # Japanese katakana ア (U+30A2) — would be 0x82 0xA0 in Shift-JIS
    katakana_a = "ア"
    # French é (U+00E9) — would be 0xE9 in cp1252/latin-1 or 0xC3 0xA9 in UTF-8
    e_acute = "é"

    person_lines = (
        f"#8997=PERSON('{cjk_he}','cjk-raw-gb18030-he','');\n"
        f"#8998=PERSON('{katakana_a}','katakana-raw-shiftjis-a','');\n"
        f"#8999=PERSON('caf{e_acute}','raw-e-acute-not-escaped','');\n"
    )
    # Also inject a PRODUCT referencing the non-ASCII name to satisfy the
    # PRODUCT byte assertion. We insert it just before ENDSEC.
    product_line = (
        f"#8996=PRODUCT('{cjk_he}','raw-locale-bytes','raw-product-name',(#9050));\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + product_line + text[idx:]


f.render = _render_with_raw_nonascii  # type: ignore[method-assign]
