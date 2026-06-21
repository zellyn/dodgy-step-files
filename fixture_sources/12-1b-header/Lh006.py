"""Lh006 — FILE_SCHEMA written without the required double parentheses (list of strings).

Catalog claim: FILE_SCHEMA's argument is a LIST OF STRING and must be written
FILE_SCHEMA(('AUTOMOTIVE_DESIGN')); — generators that emit FILE_SCHEMA('AUTOMOTIVE_DESIGN');
are non-conformant. Bug-reporter language: "FILE_SCHEMA without double parentheses",
"schema written as single string not list", "FILE_SCHEMA('AUTOMOTIVE_DESIGN') instead of list",
"FILE_SCHEMA list missing outer parens", "schema name not in list-of-string".

Reproducer recipe: FILE_SCHEMA('AUTOMOTIVE_DESIGN');

Byte assertions:
  matches(rb"FILE_SCHEMA\\s*\\(\\s*'")
  matches(rb"FILE_SCHEMA\\(\\s*'")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh006",
    defect=(
        "FILE_SCHEMA written without the required double parentheses (list of strings); "
        "input: FILE_SCHEMA argument is a bare string literal instead of a list-of-string; "
        "ISO 10303-21 §8 specifies FILE_SCHEMA with a LIST OF STRING argument, "
        "requiring double parentheses: FILE_SCHEMA(('AUTOMOTIVE_DESIGN')); "
        "generators that emit FILE_SCHEMA('AUTOMOTIVE_DESIGN'); omit the outer list "
        "parentheses, producing a grammatically invalid schema declaration; "
        "strict parsers must reject (the argument is STRING not LIST OF STRING); "
        "lenient parsers may auto-promote the bare string to a singleton list with a warning; "
        "produced by minimalist exporters and hand-rolled writers that omit the outer parens; "
        "expected kernel behavior: reject; lenient mode may auto-promote to a list with a warning; "
        "see also: Lh007, Lh008, Lh009; "
        "synonyms: FILE_SCHEMA without double parentheses, schema written as single string not list, "
        "FILE_SCHEMA list missing outer parens, schema name not in list-of-string"
    ),
)


def _render_lh006() -> str:
    """Render a Part-21 where FILE_SCHEMA uses a bare string instead of a list-of-string."""
    return (
        "ISO-10303-21;\n"
        "/* Lh006: FILE_SCHEMA argument is a bare string, not a list-of-string */\n"
        "/* ISO 10303-21 §8: FILE_SCHEMA requires LIST OF STRING: FILE_SCHEMA(('NAME')); */\n"
        "/* DEFECT: FILE_SCHEMA('AUTOMOTIVE_DESIGN'); — outer list parens are missing */\n"
        "/* Strict parsers reject; lenient parsers may auto-promote to a singleton list */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh006: FILE_SCHEMA without double parentheses'),'2;1');\n"
        "FILE_NAME('Lh006.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: bare string instead of list — missing outer parentheses around schema name */\n"
        "FILE_SCHEMA('AUTOMOTIVE_DESIGN');\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('file-schema-no-double-parens-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh006(path) -> None:
    Path(path).write_text(_render_lh006())


f.render = _render_lh006  # type: ignore[method-assign]
f.write = _write_lh006    # type: ignore[method-assign]
