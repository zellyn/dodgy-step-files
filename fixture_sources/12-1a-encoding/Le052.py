"""Le052 — \\X2\\...\\X0\\ (UCS-2) escape: whitespace splits the hex run.

Catalog claim: The hex run inside \\X2\\...\\X0\\ must be contiguous (multiple
of four hex digits). Embedding whitespace between two 4-digit groups is
malformed even if it would be a legal continuation in some Java/host string
forms.

Reproducer recipe:
  'name=\\X2\\30A2 30A4\\X0\\rest' — a space between '30A2' and '30A4'.

Byte assertions:
  contains(b'\\\\X2\\\\30A2 30A4\\\\X0\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le052",
    defect=(
        "\\X2\\...\\X0\\ (UCS-2) escape: whitespace splits the hex run; "
        "ISO 10303-21 Ed.3 §6.4.3.4: hex run inside \\X2\\...\\X0\\ must be contiguous "
        "(multiple of four hex digits); "
        "embedding whitespace between two 4-digit groups is malformed "
        "even if it would be legal in some host string forms; "
        "defect string: 'name=\\X2\\30A2 30A4\\X0\\rest' — space between '30A2' and '30A4'; "
        "receiver must emit E_BAD_X2_DIRECTIVE; "
        "reject the string or, in lenient mode, drop the whitespace and continue with a warning; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject a PERSON entity whose name string contains a \X2\
# hex run with a whitespace character breaking the contiguous hex digits.
#
# '\X2\30A2 30A4\X0\rest' is malformed: ISO 10303-21 requires the hex run
# inside \X2\...\X0\ to be a single contiguous multiple-of-four sequence.
# The space between '30A2' (katakana 'ア') and '30A4' (katakana 'ィ') splits
# the run illegally.
#
# A second PERSON entity shows the valid form for contrast.
#
# Satisfies:
#   contains(b'\\X2\\30A2 30A4\\X0\\')  — the whitespace-split hex run

_original_render = f.render


def _render_with_whitespace_split_x2() -> str:
    text = _original_render()
    person_lines = (
        # Malformed: whitespace in the middle of the \X2\ hex run
        "#8998=PERSON('name=\\X2\\30A2 30A4\\X0\\rest','whitespace-split-x2-hex','');\n"
        # Valid form for contrast: contiguous hex run (30A230A4 = 'アィ')
        "#8999=PERSON('name=\\X2\\30A230A4\\X0\\rest','contiguous-x2-hex-ok','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_whitespace_split_x2  # type: ignore[method-assign]
