"""Le054 — High-bit byte ambiguous between Windows-1252 and ISO-8859-1.

Catalog claim: Edition-2 declares ISO-8859-1 as the default 8-bit page.
Bytes 0x80-0x9F in ISO-8859-1 are C1 control characters (no glyphs); in
Windows-1252 the same range carries glyphs (Euro at 0x80, smart-quotes at
0x91-0x94, em-dash at 0x97, etc.). When a Windows-hosted writer copies
user-input strings without converting, it emits raw bytes in 0x80-0x9F into
a string literal. Strict Ed.2 readers see C1 control bytes and reject.

Reproducer recipe:
  PRODUCT.name contains \\X\\91, \\X\\92, \\X\\80, \\X\\97 —
  left/right single-quote, Euro, em-dash in Windows-1252.

Byte assertions:
  contains(b'\\\\X\\\\91') or contains(b'\\\\X\\\\92') or
    contains(b'\\\\X\\\\80') or contains(b'\\\\X\\\\97')
  matches(rb'\\\\X\\\\(80|91|92|93|94|97|99)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le054",
    defect=(
        "High-bit byte ambiguous between Windows-1252 and ISO-8859-1; "
        "ISO 10303-21 Ed.2 §6.4.3.5: default 8-bit page is ISO-8859-1; "
        "bytes 0x80-0x9F are C1 control characters in ISO-8859-1 (no glyphs); "
        "in Windows-1252 the same bytes carry printable glyphs "
        "(0x80=Euro, 0x91-0x92=smart single quotes, 0x93-0x94=smart double quotes, "
        "0x97=em-dash, 0x99=trademark); "
        "Windows-hosted writers emit raw 0x80-0x9F bytes in string literals "
        "without converting to ISO-8859-1 or \\X2\\ escapes; "
        "strict Ed.2 readers see C1 control bytes in string body and reject or corrupt; "
        "defect strings contain \\X\\91, \\X\\92, \\X\\80, \\X\\97 "
        "(the \\X\\ escape form of the ambiguous bytes); "
        "receiver must surface the ambiguity: name the byte and the page-selection policy; "
        "silent reinterpretation across vendor policies hides the disagreement; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities whose name strings contain \X\HH
# escapes for bytes in the C1 control range (0x80-0x9F). These are ambiguous
# between ISO-8859-1 (C1 control codes, no glyphs) and Windows-1252 (printable
# glyphs). The \X\ form is used (legal ISO 10303-21 syntax) to embed the
# ambiguous byte values unambiguously in the STEP text layer.
#
# 0x91 = left single quotation mark in cp1252 / C1 control in ISO-8859-1
# 0x92 = right single quotation mark in cp1252 / C1 control in ISO-8859-1
# 0x80 = Euro sign in cp1252 / undefined/PAD in ISO-8859-1
# 0x97 = em dash in cp1252 / ETB control in ISO-8859-1
#
# Satisfies:
#   contains(b'\\X\\91')                      — left smart quote byte
#   contains(b'\\X\\92')                      — right smart quote byte
#   contains(b'\\X\\80')                      — Euro sign byte
#   contains(b'\\X\\97')                      — em-dash byte
#   matches(rb'\\X\\(80|91|92|93|94|97|99)')  — C1/cp1252 range

_original_render = f.render


def _render_with_cp1252_ambiguous_bytes() -> str:
    text = _original_render()
    person_lines = (
        # Smart quotes (0x91/0x92): ambiguous Windows-1252 glyphs vs C1 controls
        "#8996=PERSON('it\\X\\92s a \\X\\91note\\X\\92','smart-quotes-cp1252-ambiguous','');\n"
        # Euro sign (0x80): printable in cp1252, undefined control in ISO-8859-1
        "#8997=PERSON('price \\X\\80 100','euro-sign-cp1252-ambiguous','');\n"
        # Em-dash (0x97): printable in cp1252, ETB control in ISO-8859-1
        "#8998=PERSON('word\\X\\97word','em-dash-cp1252-ambiguous','');\n"
        # Trademark (0x99): printable in cp1252, control in ISO-8859-1
        "#8999=PERSON('brand\\X\\99','trademark-cp1252-ambiguous','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_cp1252_ambiguous_bytes  # type: ignore[method-assign]
