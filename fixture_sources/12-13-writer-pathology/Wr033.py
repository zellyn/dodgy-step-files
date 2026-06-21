"""Wr033 — FILE_SCHEMA declares schema version that does not exist.

Catalog claim: FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 99 1 1 }')); the schema
name is recognised but the version tuple (year 99) is unparseable or refers to a
non-existent edition. Bug-reporter language: "STEP schema version unknown",
"future schema version in file".

Reproducer recipe: FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 99 1 1 }'))
where the tuple 99 is an implausible future-edition year number.

Byte assertions:
  matches(rb'\\b99\\b.*\\}')
  matches(rb'\\b99\\b')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr033",
    defect=(
        "FILE_SCHEMA declares schema version that does not exist; "
        "input: FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 99 1 1 }')); "
        "the schema name AUTOMOTIVE_DESIGN is recognised but the version tuple "
        "'{ 1 0 10303 214 99 1 1 }' uses year 99 which is unparseable / non-existent edition; "
        "produced by writers with hard-coded schema-id strings that include a future or "
        "fictional version number; "
        "receivers either reject or ignore the version and load under the last-known "
        "compatible schema; "
        "expected kernel behavior: warn on unrecognised schema version and either reject "
        "or load under the closest known schema with a diagnostic; "
        "never silently treat unknown as known; "
        "synonyms: STEP schema version unknown, future schema version in file, "
        "schema unknown to my reader"
    ),
)


def _render_wr033() -> str:
    """Render a Part-21 with a fictional schema version number."""
    return (
        "ISO-10303-21;\n"
        "/* Wr033: FILE_SCHEMA declares schema version that does not exist */\n"
        "/* Schema name AUTOMOTIVE_DESIGN is known; version tuple { 1 0 10303 214 99 1 1 } */\n"
        "/* uses year 99 — a future/fictional edition number no receiver will recognise */\n"
        "/* Writers with hard-coded schema-id strings emit implausible version tuples */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr033'),'2;1');\n"
        "FILE_NAME('Wr033.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: version tuple '{ 1 0 10303 214 99 1 1 }' does not correspond to any edition */\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 99 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('unknown-schema-version-shape',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr033(path) -> None:
    Path(path).write_text(_render_wr033())


f.render = _render_wr033  # type: ignore[method-assign]
f.write = _write_wr033    # type: ignore[method-assign]
