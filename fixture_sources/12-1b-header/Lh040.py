"""Lh040 — `FILE_INFO` Edition-3 record contradicting `FILE_NAME` date.

Catalog claim: Edition-3 FILE_INFO is intended for additional revision /
metadata that did not fit Edition-2's FILE_NAME. Producers supporting both
editions sometimes write FILE_NAME with one timestamp and FILE_INFO with a
different one, leaving the receiver to choose between them.
Bug-reporter language: "FILE_INFO contradicts FILE_NAME date", "two timestamps
disagree in header", "FILE_NAME and FILE_INFO timestamps differ", "STEP header
timestamp conflict", "Ed.3 FILE_INFO date disagrees".

Reproducer recipe:
  FILE_NAME date '2026-04-26T00:00:00'; FILE_INFO record
  ('rev','2016-01-01T00:00:00','release-r12') claiming a date 10 years earlier.

Byte assertions:
  contains(b'FILE_INFO(')
  count(b"'2026-04") + count(b"'2016-01") >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh040",
    defect=(
        "FILE_INFO Edition-3 record contradicting FILE_NAME date; "
        "input: FILE_NAME date '2026-04-26T00:00:00'; "
        "FILE_INFO record ('rev','2016-01-01T00:00:00','release-r12') "
        "claiming a date 10 years earlier; "
        "ISO 10303-21 Ed.3 §6.3: FILE_INFO is intended for additional revision/metadata "
        "that did not fit Edition-2's FILE_NAME; "
        "producers supporting both editions sometimes write FILE_NAME with one timestamp "
        "and FILE_INFO with a different one, leaving the receiver to choose between them; "
        "OCC silently picks one timestamp without surfacing the conflict; "
        "expected kernel behavior: surface both timestamps to the user; "
        "do not silently prefer one; if a single canonical date must be chosen, "
        "define the precedence rule deterministically (e.g. FILE_NAME wins for compatibility) "
        "and warn on mismatch; "
        "see also: Lh016; "
        "synonyms: FILE_INFO contradicts FILE_NAME date, two timestamps disagree in header, "
        "FILE_NAME and FILE_INFO timestamps differ, STEP header timestamp conflict, "
        "Ed.3 FILE_INFO date disagrees"
    ),
)


def _render_lh040() -> str:
    """Render a Part-21 with FILE_INFO timestamp contradicting FILE_NAME date."""
    return (
        "ISO-10303-21;\n"
        "/* Lh040: FILE_INFO timestamp contradicts FILE_NAME date */\n"
        "/* ISO 10303-21 Ed.3 §6.3: FILE_INFO provides supplementary revision metadata */\n"
        "/* DEFECT: FILE_NAME says 2026-04-26 but FILE_INFO claims 2016-01-01 (10 years earlier) */\n"
        "/* OCC silently picks one timestamp without surfacing the conflict */\n"
        "/* expected: surface both timestamps; warn on mismatch; define precedence deterministically */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh040: FILE_INFO date contradicts FILE_NAME date'),'2;1');\n"
        "FILE_NAME('Lh040.stp','2026-04-26T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "FILE_INFO('rev','2016-01-01T00:00:00','release-r12');\n"
        "/* DEFECT: FILE_INFO claims 2016-01-01 but FILE_NAME above says 2026-04-26 */\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('conflicting-timestamp-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh040(path) -> None:
    Path(path).write_text(_render_lh040())


f.render = _render_lh040  # type: ignore[method-assign]
f.write = _write_lh040    # type: ignore[method-assign]
