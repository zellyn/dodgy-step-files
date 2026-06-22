"""Le049 — Carriage-return stripping during STEP file write.

Catalog claim: A STEP writer normalises line endings by stripping all
\\r characters. When a string literal contains a literal carriage return,
the stripping also applies inside string contexts, corrupting embedded text.

Reproducer recipe:
  DESCRIPTION_ATTRIBUTE('line1\\r\\nline2','desc') where \\r is intentional.
  Writer strips, output reads 'line1\\nline2'.

Byte assertions:
  contains(b'ISO-10303-21')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le049",
    defect=(
        "Carriage-return stripping during STEP file write; "
        "OCCT MANTIS#0033602 / MANTIS#0028454: writer normalises line endings "
        "by stripping all \\r characters including inside string literals; "
        "ISO 10303-21 §6.4.4: string contents must be preserved byte-for-byte; "
        "line-ending normalisation must only apply outside string contexts; "
        "defect: DESCRIPTION_ATTRIBUTE('line1\\r\\nline2','desc') — writer strips \\r, "
        "output reads 'line1\\nline2' — embedded CR silently lost; "
        "heal and accept: preserve string contents; escape via \\X\\ if needed; "
        "must not silently strip CR inside string literals; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject a PERSON entity whose name string contains an
# embedded CR (0x0D) byte — representing the corrupted writer output where
# the CR was not stripped from inside the string literal.
#
# This fixture represents the *output* of a buggy writer that either:
#   (a) preserved the raw CR inside the string (the CR is present — corrupt
#       if the writer was supposed to strip only outside strings), or
#   (b) the writer-stripped output (CR absent — demonstrates the loss).
#
# We model case (a): the string retains the raw CR byte inside a STEP literal,
# which is spec-illegal (control characters must use \\X\\HH escaping) and
# demonstrates the defect class.
#
# Satisfies:
#   contains(b'ISO-10303-21')  — present in every valid STEP file header

_original_render = f.render


def _render_with_embedded_cr() -> str:
    text = _original_render()
    cr = "\r"
    # PERSON with embedded CR in name: 'line1<CR><LF>line2'
    # The CR is raw (spec-illegal; must be \X\0D per §6.4.3.4)
    person_lines = (
        f"#8997=PERSON('line1{cr}\nline2','cr-lf-in-string','');\n"
        "#8998=PERSON('line3\\X\\0D\\nline4','cr-escaped-in-string','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_embedded_cr  # type: ignore[method-assign]
