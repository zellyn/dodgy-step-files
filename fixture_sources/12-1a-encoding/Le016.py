"""Le016 — Single backslash inside a string literal (Windows path).

Catalog claim: The reverse-solidus is the lead-in for Part-21 control
directives; a literal backslash must be doubled (\\\\).  Generators that
copy Windows file paths verbatim emit single backslashes, which then
accidentally form what looks like a malformed \\X\\ or \\S\\ directive
(e.g. \\X1\\, \\Use...).

Reproducer recipe: 'C:\\path' (rejected by spec);
                   'C:\\Users\\Test\\X1\\file.stp' (\\X1 resembles malformed \\X\\)
                   Contrast (correct form): 'C:\\\\good\\\\path'

Byte assertions:
  matches(rb"'C:\\\\\\\\[A-Za-z]")   (two backslashes before letter = correctly-doubled form)
  count(b'C:\\\\') >= 1               (single backslash in file = defect form)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le016",
    defect=(
        "Single backslash inside a string literal (Windows file path); "
        "ISO 10303-21 §6.4.3.1: reverse-solidus is the control-directive lead-in; "
        "a literal backslash must be doubled as \\\\\\\\; "
        "Windows path generators copy verbatim single backslashes into STEP strings; "
        "'C:\\\\Users\\\\Test\\\\X1\\\\file.stp' — the \\\\X1 fragment resembles a malformed \\\\X\\\\ directive; "
        "strict mode must reject; tolerant readers must warn and must not silently "
        "consume following bytes as directive operands; "
        "round-trip must preserve literal backslashes (OCCT 7.5.0 lost them); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: PERSON entities that include:
#   #8997: 'C:\path'       — bare illegal single backslash (defect)
#   #8998: 'C:\Users\Test\X1\file.stp' — single-backslash path where \X1
#                             resembles a malformed \X\ directive (defect)
#   #8999: 'C:\\good\\path' — correctly-doubled backslashes for contrast;
#                             in the STEP file bytes this is C colon backslash backslash g..
#                             This entry satisfies matches(rb"'C:\\\\[A-Za-z]")
#
# In Python source, a single backslash in the STEP bytes must be written
# as \\ within a Python string literal (or as the character \ in a raw string).
#
# Satisfies:
#   matches(rb"'C:\\\\[A-Za-z]")  — 'C:\\good\\path' has 2 backslash bytes before 'g'
#   count(b'C:\\') >= 1           — all three entities contain C: + one-backslash

_original_render = f.render


def _render_with_windows_paths():
    text = _original_render()
    # Build STEP strings with careful byte control:
    # To emit ONE backslash in the STEP file from Python: use a single \
    # (Python will keep it verbatim in the byte sequence)
    # To emit TWO backslashes in the STEP file from Python: use \\
    person_lines = (
        # Defect: single backslash before 'p' — spec-illegal
        "#8997=PERSON('C:\\path','windows-single-backslash','');\n"
        # Defect: single backslashes throughout; \X1 fragment resembles \X\ directive
        "#8998=PERSON('C:\\Users\\Test\\X1\\file.stp','windows-x1-fragment','');\n"
        # Contrast: correctly-doubled backslashes (two backslash bytes = one literal \)
        "#8999=PERSON('C:\\\\good\\\\path','windows-doubled-backslash-correct','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_windows_paths  # type: ignore[method-assign]
