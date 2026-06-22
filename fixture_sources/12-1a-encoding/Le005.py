"""Le005 — \\X2\\…\\X0\\ (UCS-2) escape: 3 hex digits in one group.

Catalog claim: \\X2\\HHHH…\\X0\\ carries one or more 4-hex-digit UCS-2 code
units; the hex run length must be a multiple of four. This entry encodes the
3-hex-digit-group flavor (\\X2\\03B\\X0\\).

Reproducer recipe: #1=PERSON('\\X2\\03B\\X0\\'); — three hex digits between
\\X2\\ and \\X0\\.

Byte assertions:
  contains(b'\\X2\\03B\\X0\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le005",
    defect=(
        "\\X2\\ UCS-2 escape with 3-hex-digit group (not multiple of four); "
        "\\X2\\HHHH…\\X0\\ requires hex digit count divisible by four (4 digits per UCS-2 code unit); "
        "\\X2\\03B\\X0\\ has only 3 digits — the group is malformed; "
        "receiver must validate group count; emit E_BAD_X2_DIRECTIVE on malformed input; "
        "warn-and-best-effort decode without crashing; crash potential when out-of-range "
        "value fed to downstream UTF-8 encoder; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject a PERSON entity with a 3-hex-digit \\X2\\ group via
# render() override. The \\X2\\03B\\X0\\ sequence has only 3 hex digits between
# the opening \\X2\\ and closing \\X0\\; spec requires a multiple of 4 (one
# 16-bit UCS-2 code unit per 4-digit group). A parser that does not validate
# the digit count may read past the group boundary or produce a wrong codepoint.
#
# Satisfies: contains(b'\\X2\\03B\\X0\\')

_original_render = f.render


def _render_with_bad_x2_escape():
    text = _original_render()
    # PERSON with 3-digit \\X2\\ group: 03B is Greek lowercase beta (β) truncated
    # (the full 4-digit code would be 03B2, but \\X2\\03B is cut short by one digit)
    person_line = "#8999=PERSON('\\X2\\03B\\X0\\','three-digit-ucs2-group','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_bad_x2_escape  # type: ignore[method-assign]
