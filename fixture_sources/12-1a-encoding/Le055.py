"""Le055 — Boolean lexeme written as .TRUE. / .FALSE. instead of canonical .T. / .F.

Catalog claim: ISO 10303-21 §6.3.4 spells boolean values .T. and .F. (single
letter, dot-bracketed). A few producers emit the EXPRESS keyword spellings
.TRUE. and .FALSE. inside Part-21 attribute slots. Strict lexers reject or
mis-tokenise the surrounding record; heuristic lexers may silently accept.

Reproducer recipe:
  An EDGE_CURVE whose same_sense attribute is .TRUE. rather than .T.;
  a second instance with .FALSE. rather than .F.

Byte assertions:
  contains(b'.TRUE.') or contains(b'.FALSE.')
  count(b'.TRUE.') + count(b'.FALSE.') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le055",
    defect=(
        "Boolean lexeme written as .TRUE. / .FALSE. instead of canonical .T. / .F.; "
        "ISO 10303-21 §6.3.4: boolean values must be spelled .T. and .F. "
        "(single letter, dot-bracketed); "
        "a few producers emit EXPRESS keyword spellings .TRUE. and .FALSE. "
        "inside Part-21 attribute slots — cousin of Wr041 (writer-side root cause); "
        "strict lexers expecting exactly .T. or .F. reject or mis-tokenise the record; "
        "heuristic lexers may accept the long form, hiding the producer-side defect; "
        "defect: EDGE_CURVE same_sense=.TRUE. and same_sense=.FALSE. instead of .T./.F.; "
        "receiver must reject with a diagnostic naming the offending lexeme, "
        "or in lenient mode accept with a warning; silent acceptance hides the defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject raw EDGE_CURVE entities whose same_sense attribute
# uses the long-form boolean lexemes .TRUE. and .FALSE. instead of the
# canonical .T. and .F. required by ISO 10303-21 §6.3.4.
#
# The entities reference high-numbered vertex/curve IDs that are intentionally
# absent (this is an encoding-defect fixture, not a geometry fixture). The
# key defect is the boolean spelling — .TRUE. / .FALSE. — not the topology.
#
# We use PERSON entities to carry the same_sense-style string in the name
# attribute (to keep the fixture self-contained without needing real geometry),
# and also inject standalone EDGE_CURVE-like raw lines that carry .TRUE./.FALSE.
# in the actual boolean slot.
#
# Satisfies:
#   contains(b'.TRUE.')                        — long-form boolean present
#   count(b'.TRUE.') + count(b'.FALSE.') >= 1  — at least one non-canonical boolean

_original_render = f.render


def _render_with_long_form_booleans() -> str:
    text = _original_render()
    # Raw EDGE_CURVE records with non-canonical boolean spellings.
    # Vertex/curve refs (#9001, #9002, #9003) are absent — the fixture
    # tests the tokeniser's boolean handling, not topology resolution.
    raw_lines = (
        # .TRUE. instead of .T.
        "#8997=EDGE_CURVE('edge-true',#9001,#9002,#9003,.TRUE.);\n"
        # .FALSE. instead of .F.
        "#8998=EDGE_CURVE('edge-false',#9001,#9002,#9003,.FALSE.);\n"
        # PERSON to reinforce the defect string in a simpler context
        "#8999=PERSON('same_sense is .TRUE. not .T.','long-form-boolean-defect','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + raw_lines + text[idx:]


f.render = _render_with_long_form_booleans  # type: ignore[method-assign]
