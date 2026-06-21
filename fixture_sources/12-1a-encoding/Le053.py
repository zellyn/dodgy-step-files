"""Le053 — \\X2\\...\\X0\\ (UCS-2) escape: nested \\X2\\ opened without closing the prior.

Catalog claim: \\X2\\...\\X0\\ directives are not re-entrant. Opening a fresh
\\X2\\ while another is still active is malformed; a naive scanner may merge
the two hex runs or lose the inner content.

Reproducer recipe:
  'name=\\X2\\30A2\\X2\\30A4\\X0\\' — second \\X2\\ opens before the first closes.

Byte assertions:
  contains(b'\\\\X2\\\\30A2\\\\X2\\\\30A4\\\\X0\\\\')
  count(b'\\\\X2\\\\') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le053",
    defect=(
        "\\X2\\...\\X0\\ (UCS-2) escape: nested \\X2\\ opened without closing the prior; "
        "ISO 10303-21 Ed.3 §6.4.3.4: \\X2\\...\\X0\\ directives are not re-entrant; "
        "opening a fresh \\X2\\ while another is still active is malformed; "
        "a naive scanner may merge the two hex runs or lose the inner content; "
        "defect string: 'name=\\X2\\30A2\\X2\\30A4\\X0\\' — second \\X2\\ opens before first closes; "
        "receiver must emit E_BAD_X2_DIRECTIVE (nested); "
        "reject the string without crashing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject a PERSON entity whose name string opens a second
# \X2\ directive while the first is still active (no intervening \X0\).
#
# '\X2\30A2\X2\30A4\X0\' is malformed: only one \X0\ closes both, but
# the spec requires \X2\ to be non-re-entrant. 30A2 = katakana 'ア',
# 30A4 = katakana 'ィ'.
#
# A second PERSON entity shows the valid form (two separate properly-closed
# \X2\...\X0\ groups) for contrast.
#
# Satisfies:
#   contains(b'\\X2\\30A2\\X2\\30A4\\X0\\')  — nested \X2\ without intervening \X0\
#   count(b'\\X2\\') >= 2                      — at least two \X2\ occurrences

_original_render = f.render


def _render_with_nested_x2() -> str:
    text = _original_render()
    person_lines = (
        # Malformed: second \X2\ opens before first closes
        "#8998=PERSON('name=\\X2\\30A2\\X2\\30A4\\X0\\','nested-x2-no-x0-between','');\n"
        # Valid form for contrast: two separate \X2\...\X0\ blocks
        "#8999=PERSON('name=\\X2\\30A2\\X0\\mid\\X2\\30A4\\X0\\','separate-x2-blocks-ok','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_nested_x2  # type: ignore[method-assign]
