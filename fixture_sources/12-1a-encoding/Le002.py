"""Le002 — Edition-default encoding mismatch (Ed.2 ISO-8859-1 vs Ed.3 UTF-8).

Catalog claim: Edition 2 declares ISO-8859-1 as the default character set;
non-ASCII octets must be expressed via \\X\\, \\X2\\, or page-shift directives.
Edition 3 changes the default to UTF-8. A file produced under one edition and
read by a tool assuming the other interprets non-ASCII bytes incorrectly. An
Ed.3 file using only Ed.2-style \\X\\E9 escapes is lawful but is sometimes
mis-decoded by parsers that strictly assume raw UTF-8.

Reproducer recipe: an Ed.3 file body containing the raw bytes 0xC3 0xA9 for
"é"; or an Ed.2 file using '\\X\\E9' read by an Ed.3-only tool.

Byte assertions:
  contains(b'\\X\\E9')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le002",
    defect=(
        "Edition-default encoding mismatch: Ed.2 ISO-8859-1 vs Ed.3 UTF-8; "
        "Ed.2 file uses \\X\\E9 escape for U+00E9 (e-acute); "
        "Ed.3-only parser reads raw UTF-8 and misinterprets the \\X\\E9 escape; "
        "receiver must inspect FILE_DESCRIPTION implementation_level to determine edition; "
        "accept both forms regardless and never assume file declares its encoding; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: parser must accept the file but OCC must
# yield no shape (occt=empty/empty per catalog). Omit add_product_chain so
# there is no PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry
# from — only the encoding-defective DATA bytes remain. A single
# GEOMETRIC_CURVE_SET preserves a parseable DATA section without giving
# OCC anything to load.
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Encoding defect payload: inject the Ed.2 \\X\\E9 escape sequence into a
# PERSON entity in the DATA section via render() override. The \\X\\E9 byte
# sequence is an Ed.2-style ISO-8859-1 escape for U+00E9 (é). An Ed.3-only
# parser that expects raw UTF-8 will either reject the escape or misinterpret
# the bytes that follow.
#
# Satisfies: contains(b'\\X\\E9')

_original_render = f.render


def _render_with_edition_mismatch():
    text = _original_render()
    # Inject a PERSON entity using the Ed.2 \\X\\E9 escape for é (e-acute)
    # into the DATA section. The PERSON name 'caf\X\E9' means "café" in
    # ISO-8859-1 encoding (Edition 2 style). An Edition 3 parser expecting
    # raw UTF-8 (where é = 0xC3 0xA9) will misread or reject the \\X\\ escape.
    person_line = "#8999=PERSON('caf\\X\\E9','Caf\\X\\E9','');\n"
    # Insert just before ENDSEC at the end of DATA section
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_edition_mismatch  # type: ignore[method-assign]
