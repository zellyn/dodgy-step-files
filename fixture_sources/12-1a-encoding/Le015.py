"""Le015 — Unterminated string literal.

Catalog claim: a string with an opening apostrophe but no matching close advances
the scanner past the end of the intended attribute and may swallow the rest of the
file or read sensitive memory until a lucky ' byte is found.

Byte assertions: matches(rb"'unclosed_string_then_eof"), not_contains(b'END-ISO-10303-21;'),
                 matches(rb"#20=PERSON\\(")
Tier-3: load != "ok"
Expected: occt=reject/reject gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le015",
    defect=(
        "Unterminated string literal at EOF: PERSON entity opens an apostrophe "
        "and never closes it; no trailing parameters, no semicolon, no ENDSEC, "
        "no file-footer; a bounded scanner must emit E_UNTERMINATED_STRING; "
        "the open-quote IS the mechanism; file is intentionally truncated after "
        "the opening apostrophe of the unclosed string"
    ),
)

# Anchor geometry: CARTESIAN_POINTs + AXIS2_PLACEMENT_3D so the file is well-formed
# up to the defect point
p0  = f.cartesian_point((0.0, 0.0, 0.0))
zd  = f.direction((0.0, 0.0, 1.0))
xd  = f.direction((1.0, 0.0, 0.0))
f.axis2_placement_3d(p0, zd, xd)

_original_render = f.render


def _render_with_unterminated_string():
    text = _original_render()
    # Replace the END-ISO-10303-21 footer with the PERSON entity that
    # opens a string that never closes. The file ends mid-literal at EOF.
    # #20=PERSON('p1','unclosed_string_then_eof
    # The literal opening quote on the 'unclosed_string_then_eof is the defect.
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    # Inject PERSON with unclosed string and stop — no ENDSEC, no footer
    return text[:idx] + "\n#20=PERSON('p1','unclosed_string_then_eof"


f.render = _render_with_unterminated_string  # type: ignore[method-assign]
