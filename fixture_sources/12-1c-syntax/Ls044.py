"""Ls044 — String concatenation across consecutive literals (not allowed).

Catalog claim: Unlike C, Part 21 does not concatenate adjacent string literals.
`'foo' 'bar'` is two strings, not one. Generators that line-wrap long strings by
writing two consecutive literals corrupt the data when the position expects exactly
one STRING.

Reproducer recipe: `FILE_DESCRIPTION(('first part' ' second part'),'2;1');`

Byte assertions:
  matches(rb"'[^']+'\s+'[^']+'")
  matches(rb"'[^']{2,}'\s+'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls044",
    defect=(
        "Adjacent consecutive string literals — Part 21 does not concatenate them; "
        "unlike C, ISO 10303-21 does not concatenate adjacent string literals; "
        "'foo' 'bar' is two strings, not one concatenated string; "
        "generators that line-wrap long strings by writing two consecutive literals "
        "corrupt the data when the position expects exactly one STRING; "
        "defect 1: FILE_DESCRIPTION has two adjacent string literals "
        "in a slot that expects one — 'first part' ' second part'; "
        "when the grammar expects a single STRING, the second literal is a parse error; "
        "when the position is LIST OF STRING, accepting both as two elements "
        "is a semantic error (likely unintended); "
        "defect 2: in a PRODUCT entity, the description attribute is split "
        "across two adjacent literals; "
        "expected kernel behavior: reject adjacent literals in a single-STRING slot; "
        "warn when accepted as two elements in a list; "
        "synonyms: adjacent STEP string literals, two strings line-wrap into one slot, "
        "C-style string concatenation in STEP, STEP string concatenation not allowed, "
        "consecutive literals corrupt data; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_adjacent_string_literals() -> str:
    header = f._render_header()
    return (
        "/* Ls044 - String concatenation across consecutive literals (not allowed)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c string-quoting (impacts grammar shape)\n"
        "   Sources         : N055\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Unlike C, Part 21 does not concatenate adjacent string literals.\n"
        "     'foo' 'bar' is two strings, not one. Generators that line-wrap long\n"
        "     strings by writing two consecutive literals corrupt the data when the\n"
        "     position expects exactly one STRING.\n"
        "   Expected behavior\n"
        "     Reject adjacent literals in a single-STRING slot.\n"
        "     When position is LIST OF STRING, accept as two elements but warn.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "/* Defect 1: FILE_DESCRIPTION list has two adjacent literals in one slot */\n"
        "FILE_DESCRIPTION(('first part' ' second part'),'2;1');\n"
        "FILE_NAME('Ls044.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "#3=VECTOR('v',#2,1.);\n"
        "/* Defect 2: PRODUCT description split across two adjacent string literals */\n"
        "#4=PRODUCT('part-001','a very long product ' 'description that was line-wrapped','',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_adjacent_string_literals  # type: ignore[method-assign]
