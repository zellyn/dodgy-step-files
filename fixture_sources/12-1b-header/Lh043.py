"""Lh043 — Header `FILE_DESCRIPTION` with comments inside string.

Catalog claim: A `FILE_DESCRIPTION` record's strings contain `/* */` sequences
that legacy readers strip as comments. The result is corrupted description
content and possibly truncated header records.
Bug-reporter language: "FILE_DESCRIPTION string contains comment",
"/* inside FILE_DESCRIPTION string", "embedded comment in header literal",
"STEP comment inside string", "header description with comment characters".

Reproducer recipe:
  FILE_DESCRIPTION(('Test /* note */ part'),'2;1'); — reader strips
  /* note */ from inside the description string.

Byte assertions:
  matches(rb"FILE_DESCRIPTION\\(\\([^)]*\\/\\*[^)]*\\*\\/[^)]*\\)")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh043",
    defect=(
        "Header FILE_DESCRIPTION with comments inside string; "
        "input: FILE_DESCRIPTION(('Test /* note */ part'),'2;1'); "
        "where /* note */ appears inside the description string literal; "
        "ISO 10303-21: comment sequences /* */ are block comments only outside string literals; "
        "legacy readers that strip /* */ without tracking string context corrupt the description "
        "content and may truncate header records; "
        "pure-Python Part-21 validator accepts; "
        "OCC rejects the file; "
        "expected kernel behavior: heal and accept; "
        "comment-stripping must never apply inside string literals; "
        "bracket comment characters with string-context state machine; "
        "see also: Ad097, Le029; "
        "synonyms: FILE_DESCRIPTION string contains comment, /* inside FILE_DESCRIPTION string, "
        "embedded comment in header literal, STEP comment inside string, "
        "header description with comment characters"
    ),
)


def _render_lh043() -> str:
    """Render a Part-21 with /* */ comment characters inside FILE_DESCRIPTION string."""
    return (
        "ISO-10303-21;\n"
        "/* Lh043: FILE_DESCRIPTION string containing embedded comment sequence /* note */ */\n"
        "/* ISO 10303-21: comment sequences /* */ apply only outside string literals */\n"
        "/* DEFECT: legacy readers strip /* note */ from inside the string, corrupting content */\n"
        "/* pure-Python validator accepts; OCC rejects; expected: heal and accept */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Test /* note */ part description'),'2;1');\n"
        "/* DEFECT: /* note */ inside the string literal above must NOT be stripped as a comment */\n"
        "FILE_NAME('Lh043.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('comment-in-string-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh043(path) -> None:
    Path(path).write_text(_render_lh043())


f.render = _render_lh043  # type: ignore[method-assign]
f.write = _write_lh043    # type: ignore[method-assign]
