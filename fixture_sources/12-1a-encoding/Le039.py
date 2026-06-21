"""Le039 — \\PE\\ selector letter outside the legal A-I range.

Catalog claim: ISO 10303-21 Edition 3 §6.4.3 defines \\PE\\ as an
alphabet-extension directive whose follow byte must be a letter in the
range A-I, each naming one of the nine defined ISO 8859 supplementary
code pages. An operand outside that range (e.g. 'Z') does not name
any defined page; the receiver must reject or warn-and-proceed.

Reproducer recipe:
  PRODUCT.name='bad=\\PE\\Z\\S\\xx' — operand 'Z' is not in the legal
  selector range A-I.

Byte assertions:
  contains(b'\\\\PE\\\\Z')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le039",
    defect=(
        "\\PE\\ selector letter outside the legal A-I range; "
        "ISO 10303-21 Ed.3 §6.4.3: \\PE\\ must be followed by exactly one "
        "letter in A-I naming one of the nine ISO 8859 supplementary code pages; "
        "operand 'Z' (and any letter outside A-I) does not name a defined page; "
        "a receiver must reject the directive or emit a diagnostic and fall back; "
        "defect string: 'bad=\\PE\\Z\\S\\xx' — the operand 'Z' is out-of-range; "
        "parsers that silently accept 'Z' as a code-page selector produce "
        "wrong glyphs or pass the directive bytes through verbatim; "
        "the out-of-range letter may cause the lexer to desynchronise "
        "if it treats the following byte as the next token start; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities with out-of-range \\PE\\ selectors.
#
# PERSON #8998: name = 'bad=\PE\Z\S\xx'
#   \\PE\\Z — operand 'Z' is not in A-I; no defined code page with that letter.
#   The \\S\\xx bytes would be interpreted against an undefined page.
#
# PERSON #8999: name = 'also=\PE\M\S\yy'
#   \\PE\\M — operand 'M' is also outside the legal A-I range; demonstrates
#   that multiple out-of-range letters all trigger the same defect class.
#
# Satisfies:
#   contains(b'\\PE\\Z')  — primary byte assertion

_original_render = f.render


def _render_with_pe_out_of_range_selector() -> str:
    text = _original_render()
    person_lines = (
        # \\PE\\Z: out-of-range selector; 'Z' does not name any ISO 8859 page
        "#8998=PERSON('bad=\\PE\\Z\\S\\xx','pe-selector-out-of-range-Z','');\n"
        # \\PE\\M: second out-of-range selector; 'M' is also outside A-I
        "#8999=PERSON('also=\\PE\\M\\S\\yy','pe-selector-out-of-range-M','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_pe_out_of_range_selector  # type: ignore[method-assign]
