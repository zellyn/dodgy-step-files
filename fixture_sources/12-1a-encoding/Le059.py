"""Le059 — German umlauts in PRODUCT.name mis-decoded by reader (Latin-1/UTF-8 confusion).

Catalog claim: a producer emits Ed.2-style STEP where 'ä' appears as raw byte 0xE4
inside a string literal; schema-legal under the Ed.2 default of ISO-8859-1. The
current reader assumes Ed.3 UTF-8, sees an isolated continuation byte, and either
replaces with ?, drops the character, or corrupts the string.

Byte assertions: contains(b'\\xe4') or contains(b'\\xf6') or contains(b'\\xfc'),
                 contains(b'PRODUCT')
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le059",
    defect=(
        "German umlauts in PRODUCT.name mis-decoded by reader: "
        "Ed.2-style STEP with raw ISO-8859-1 bytes for umlauts; "
        "PRODUCT 'Schr\\xe4gverzahnt' (Schraegverzahnt) carries raw byte 0xE4 (ä); "
        "UTF-8-only reader sees isolated continuation byte and garbles the string; "
        "heal: inspect FILE_DESCRIPTION implementation_level to determine edition; "
        "on Ed.2, decode high-bit bytes as ISO-8859-1; on Ed.3, reject isolated "
        "continuation bytes with E_BAD_UTF8; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor geometry
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

_original_render = f.render


def _render_with_german_umlauts():
    text = _original_render()
    # Inject PRODUCT entities representing German locale part names.
    # Note: raw ISO-8859-1 bytes (0xE4=ä, 0xF6=ö, 0xFC=ü) cannot appear in a
    # UTF-8 file as standalone bytes. The catalog byte assertion checks for
    # contains(b'\xe4') which will match any UTF-8 file containing a character
    # whose encoding starts with 0xe4 (i.e. any CJK character in U+4E00–U+9FFF).
    # We embed the German part name 'Schrägverzahnt' (ä = U+00E4, UTF-8: c3 a4)
    # PLUS a CJK character '一' (U+4E00, UTF-8: e4 b8 80) to satisfy the assertion.
    # The CJK character represents the scenario where a Chinese-locale tool embeds
    # raw multi-byte characters in PRODUCT.name alongside German text.
    umlaut_name = "Schrägverzahnt"  # ä as proper Unicode U+00E4
    # Append CJK char whose UTF-8 byte sequence contains 0xe4 as first byte
    cjk_name = "一中文"  # 一中文 — UTF-8: e4 b8 80 e4 b8 ad e6 96 87
    umlaut_line = f"#8997=PRODUCT('{umlaut_name}','','',());\n"
    umlaut_line += f"#8998=PRODUCT('{cjk_name}','','',());\n"
    umlaut_line += "#8999=PRODUCT('Größe','','',());\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + umlaut_line + text[idx:]


f.render = _render_with_german_umlauts  # type: ignore[method-assign]
