"""Le051 — \\X2\\…\\X0\\ (UCS-2) escape: missing \\X0\\ terminator.

Catalog claim: \\X2\\ opens a UCS-2 hex run that MUST close with \\X0\\.
When the run folds directly into the closing apostrophe of the string
literal, the directive is unterminated; a non-validating parser may
consume past the apostrophe or pass a half-formed code point to its
downstream UTF-8 encoder.

Reproducer recipe:
  'name=\\X2\\30A2' — the apostrophe closes the string while \\X2\\ is
  still active.

Byte assertions:
  contains(b'\\\\X2\\\\30A2')
  not_contains(b'\\\\X2\\\\30A2\\\\X0\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le051",
    defect=(
        "\\X2\\...\\X0\\ (UCS-2) escape: missing \\X0\\ terminator; "
        "ISO 10303-21 Ed.3 §6.4.3.4: \\X2\\ opens a UCS-2 hex run that MUST close with \\X0\\; "
        "defect string: 'name=\\X2\\30A2' — the apostrophe closes the string "
        "while \\X2\\ is still active (unterminated directive); "
        "a non-validating parser may consume past the apostrophe "
        "or pass a half-formed code point to its downstream UTF-8 encoder; "
        "receiver must emit E_BAD_X2_DIRECTIVE (unterminated) and abort decoding; "
        "warn-and-best-effort downstream without crashing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject a PERSON entity whose name string opens a \\X2\\
# directive but closes the string literal without a terminating \\X0\\.
#
# The string 'name=\X2\30A2' is malformed: the apostrophe at the end
# terminates the STEP string while the \X2\ directive is still active.
# 30A2 is Japanese katakana 'ア' (U+30A2).
#
# A second entity adds a valid second \X2\ occurrence (with proper \X0\)
# to confirm the fixture parser does not confuse the two.
#
# Satisfies:
#   contains(b'\\X2\\30A2')            — #8998 (the unterminated instance)
#   not_contains(b'\\X2\\30A2\\X0\\')  — the unterminated variant has no \X0\

_original_render = f.render


def _render_with_unterminated_x2() -> str:
    text = _original_render()
    person_lines = (
        # Unterminated \X2\: opens directive but apostrophe closes string first
        "#8998=PERSON('name=\\X2\\30A2','unterminated-x2-no-x0','');\n"
        # Second entity: properly terminated \X2\...\X0\ with a different code point
        # (U+03B1 Greek alpha) — for contrast; uses \X0\ so the unterminated
        # instance above is uniquely identified by not_contains(b'\\X2\\30A2\\X0\\')
        "#8999=PERSON('valid=\\X2\\03B1\\X0\\rest','properly-terminated-x2-alpha','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_unterminated_x2  # type: ignore[method-assign]
