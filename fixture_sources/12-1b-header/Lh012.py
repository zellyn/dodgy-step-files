"""Lh012 — Unquoted timestamp in FILE_NAME (timestamp not a STRING).

Catalog claim: Per ISO 10303-21 the timestamp attribute of FILE_NAME is a STRING.
Some generators write it without surrounding apostrophes:
FILE_NAME('out.stp',2013-10-24T12:12:06,..);
The bare token tokenizes as identifiers/numbers and fails grammar.
Bug-reporter language: "unquoted timestamp in FILE_NAME", "STEP date without apostrophes",
"bare timestamp parses as identifier", "FILE_NAME date not a STRING",
"timestamp tokenizes as numbers".

Reproducer recipe: FILE_NAME('out.stp',2013-10-24T12:12:06,(''),(''),'writer','','');

Byte assertions:
  matches(rb"FILE_NAME\\(\\s*'[^']*'\\s*,\\s*[0-9]{4}-[0-9]{2}-[0-9]{2}T")
  matches(rb"FILE_NAME\\([^;]*,\\s*\\d{4}-\\d{2}-\\d{2}T")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh012",
    defect=(
        "Unquoted timestamp in FILE_NAME (timestamp not a STRING); "
        "input: FILE_NAME timestamp attribute is written as a bare token "
        "2013-10-24T12:12:06 without surrounding apostrophes; "
        "ISO 10303-21 §8 specifies the timestamp as a STRING (apostrophe-delimited); "
        "the bare ISO-8601 token tokenizes as a sequence of integers and minus-operators "
        "causing a grammar error; "
        "produced by older stepcode versions (issue #267) that omit apostrophes around "
        "the datetime value; "
        "expected kernel behavior: reject with 'expected STRING at attribute 2' pointing "
        "at the unquoted token; offer strict/lenient toggle that re-quotes ISO-8601-shaped "
        "tokens with a warning; "
        "see also: Lh011; "
        "synonyms: unquoted timestamp in FILE_NAME, STEP date without apostrophes, "
        "bare timestamp parses as identifier, FILE_NAME date not a STRING, "
        "timestamp tokenizes as numbers"
    ),
)


def _render_lh012() -> str:
    """Render a Part-21 where FILE_NAME timestamp is not quoted as a STRING."""
    return (
        "ISO-10303-21;\n"
        "/* Lh012: FILE_NAME timestamp is a bare token, not a quoted STRING */\n"
        "/* ISO 10303-21 §8: timestamp attribute of FILE_NAME must be a STRING (apostrophe-delimited) */\n"
        "/* DEFECT: 2013-10-24T12:12:06 lacks surrounding apostrophes */\n"
        "/* The bare token tokenizes as identifiers/numbers and fails the Part-21 grammar */\n"
        "/* Produced by older stepcode versions (issue #267) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh012: unquoted timestamp in FILE_NAME - timestamp not a STRING'),'2;1');\n"
        "/* DEFECT: timestamp 2013-10-24T12:12:06 is a bare token, not a quoted STRING */\n"
        "FILE_NAME('Lh012.stp',2013-10-24T12:12:06,(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('unquoted-timestamp-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh012(path) -> None:
    Path(path).write_text(_render_lh012())


f.render = _render_lh012  # type: ignore[method-assign]
f.write = _write_lh012    # type: ignore[method-assign]
