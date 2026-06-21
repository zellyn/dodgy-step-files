"""Lh011 — FileTimeStamp not in ISO-8601 form.

Catalog claim: FILE_NAME's timestamp attribute must be ISO-8601 (YYYY-MM-DDThh:mm:ss[±hh:mm]).
Producers emit RFC 822 dates, locale-formatted ('27/12/2003 11:57', '08/13/2014'),
epoch integers, or empty strings. Bug-reporter language: "FILE_NAME timestamp not ISO-8601",
"RFC 822 date in STEP header", "STEP timestamp 27/12/2003 format",
"epoch integer in FILE_NAME timestamp", "locale-formatted date in header".

Reproducer recipe: FILE_NAME('a.stp','27/12/2003 11:57',..);

Byte assertions:
  matches(rb"FILE_NAME\\([^;]*'[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh011",
    defect=(
        "FileTimeStamp not in ISO-8601 form in FILE_NAME; "
        "input: FILE_NAME timestamp attribute contains a locale-formatted date "
        "'27/12/2003 11:57' instead of the required ISO-8601 form YYYY-MM-DDThh:mm:ss; "
        "ISO 10303-21 §8 specifies the FILE_NAME timestamp as an ISO-8601 datetime string; "
        "producers emit RFC 822 dates, locale-formatted slash-separated dates, "
        "epoch integers, or empty strings; "
        "receivers that parse the timestamp for semantic purposes (e.g. file age, "
        "reproducible builds, delta detection) will fail or produce incorrect results; "
        "the value is lexically valid as a STEP STRING so the file may parse successfully, "
        "but the semantic layer should warn; "
        "produced by older CAD exporters and translators that use system locale date formatting; "
        "expected kernel behavior: warn and accept; do not reject on non-conformant timestamp; "
        "see also: Lh012, Lh013; "
        "synonyms: FILE_NAME timestamp not ISO-8601, RFC 822 date in STEP header, "
        "STEP timestamp 27/12/2003 format, epoch integer in FILE_NAME timestamp, "
        "locale-formatted date in header"
    ),
)


def _render_lh011() -> str:
    """Render a Part-21 where FILE_NAME timestamp is locale-formatted instead of ISO-8601."""
    return (
        "ISO-10303-21;\n"
        "/* Lh011: FILE_NAME timestamp is locale-formatted (DD/MM/YYYY HH:MM), not ISO-8601 */\n"
        "/* ISO 10303-21 §8: timestamp must be ISO-8601 form YYYY-MM-DDThh:mm:ss */\n"
        "/* DEFECT: '27/12/2003 11:57' is a locale-formatted date, not ISO-8601 */\n"
        "/* File parses (STRING is lexically valid) but semantic layer must warn */\n"
        "/* Produced by older CAD exporters that use system locale date formatting */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh011: FILE_NAME timestamp not in ISO-8601 form'),'2;1');\n"
        "/* DEFECT: timestamp '27/12/2003 11:57' is DD/MM/YYYY HH:MM format, not ISO-8601 */\n"
        "FILE_NAME('Lh011.stp','27/12/2003 11:57',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('non-iso8601-timestamp-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh011(path) -> None:
    Path(path).write_text(_render_lh011())


f.render = _render_lh011  # type: ignore[method-assign]
f.write = _write_lh011    # type: ignore[method-assign]
