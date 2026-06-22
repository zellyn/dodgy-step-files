"""Le012 — Unrecognised backslash control directive in a string.

Catalog claim: A string contains a backslash directive that is not one of the
spec-recognised forms (\\X\\, \\X2\\…\\X0\\, \\X4\\…\\X0\\, \\S\\x, \\Q\\x,
\\PE\\, \\N\\n, \\F\\). The defect is embedding \\Z\\ or \\M\\ in a string
attribute where no such directive is defined by the standard.

Reproducer recipe:
  embed 'foo\\Z\\bar' in a string-valued attribute

Byte assertions:
  contains(b'\\\\Z\\\\') or contains(b'\\\\M\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le012",
    defect=(
        "Unrecognised backslash control directive in a string attribute; "
        "spec-recognised directives: \\X\\, \\X2\\, \\X4\\, \\S\\, \\Q\\, \\PE\\, \\N\\, \\F\\; "
        "defect 1: 'foo\\Z\\bar' — \\Z\\ is not defined in ISO 10303-21 Table 4; "
        "defect 2: 'abc\\M\\def' — \\M\\ is also not a recognised directive; "
        "these may be vendor extensions; a strict receiver must reject; "
        "a tolerant receiver must pass the bytes through literally with a warning; "
        "silently accepting without diagnostics is a kernel bug; "
        "malformed directive leaves the affected string attribute either truncated "
        "or containing wrong code points; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: two PERSON entities using non-spec backslash directives via
# render() override.
#
# PERSON #8998: 'foo\\Z\\bar' — \\Z\\ is not a recognised Part-21 directive.
# PERSON #8999: 'abc\\M\\def' — \\M\\ is also not a recognised Part-21 directive.
#
# Satisfies:
#   contains(b'\\Z\\')  — #8998
#   contains(b'\\M\\')  — #8999

_original_render = f.render


def _render_with_unknown_directive():
    text = _original_render()
    person_lines = (
        # \\Z\\ is not defined in ISO 10303-21 §6.4.3 Table 4
        "#8998=PERSON('foo\\Z\\bar','unknown-Z-directive','');\n"
        # \\M\\ is also not a recognised directive
        "#8999=PERSON('abc\\M\\def','unknown-M-directive','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_unknown_directive  # type: ignore[method-assign]
