"""Le026 — \\X0\\ end-marker missing — remainder treated as encoded content.

Catalog claim: When \\X0\\ is omitted, OCCT (pre-fix) treated the remainder
of the string as encoded hex content, garbling the trailing ASCII portion
of the literal. A receiver must warn and best-effort decode the Unicode
chars present; revert to literal-ASCII mode at the closing apostrophe.

Reproducer recipe:
  name = '\\X2\\00B0'  (closing apostrophe immediately follows hex run; no \\X0\\)

Byte assertions:
  contains(b'\\X2\\00B0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le026",
    defect=(
        "\\X2\\ escape block missing \\X0\\ end-marker; "
        "ISO 10303-21 §6.4.3.3: \\X2\\HHHH...\\X0\\ — the \\X0\\ is mandatory; "
        "when \\X0\\ is absent the remainder of the string literal is treated as "
        "encoded hex content, garbling any trailing ASCII characters; "
        "OCCT pre-fix (StepData_StepReaderData.cxx:197-213) exhibited this garbling; "
        "defect: '\\X2\\00B0' — degree symbol U+00B0 encoded but no \\X0\\ follow; "
        "closing apostrophe immediately follows the hex run without the terminator; "
        "receiver must warn and best-effort decode without crashing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities whose name strings use \\X2\\ without
# the mandatory \\X0\\ terminator.
#
# PERSON #8997: '\\X2\\00B0' — U+00B0 DEGREE SIGN encoded as \\X2\\00B0 but
#   the \\X0\\ end-marker is absent; the closing apostrophe abuts the hex run.
#   A pre-fix OCCT parser would treat the apostrophe as additional hex content
#   and garble the attribute value.
#
# PERSON #8998: '\\X2\\03B1 rad' — \\X2\\ block for Greek alpha (U+03B1) is
#   followed by literal ASCII " rad" but has no \\X0\\ to switch modes back;
#   the " rad" suffix would be misinterpreted as hex digits (space=0x20, etc.)
#   by a naive state machine.
#
# Satisfies:
#   contains(b'\\X2\\00B0')   — #8997

_original_render = f.render


def _render_with_missing_x0() -> str:
    text = _original_render()
    # In the STEP file, backslash is a literal backslash.
    # Python raw strings: r'\X2\00B0' produces the 9-char sequence \X2\00B0
    # which is what must appear in the .stp bytes.
    person_lines = (
        r"#8997=PERSON('\X2\00B0','degree-no-x0-terminator','');" + "\n"
        r"#8998=PERSON('\X2\03B1 rad','alpha-suffix-no-x0','');" + "\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_missing_x0  # type: ignore[method-assign]
