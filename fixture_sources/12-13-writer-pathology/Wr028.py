"""Wr028 — FILE_NAME.author and originating_system fields blank or auto-filled with placeholder.

Catalog claim: FILE_NAME records author=(''), organization=(''), originating_system='',
authorisation=''. The file is well-formed; provenance and audit-trail are lost.
Bug-reporter language: "STEP has no author", "can't tell who created this STEP",
"lost provenance".

Reproducer recipe: standard FILE_NAME with all author/org/system fields as empty strings.

Byte assertions:
  matches(rb"(?s)FILE_NAME\\([^;]*\\(''\\)[^;]*'','',''")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr028",
    defect=(
        "FILE_NAME.author and originating_system fields blank or auto-filled with placeholder; "
        "input: FILE_NAME records author=(''), organization=(''), originating_system='', "
        "authorisation=''; the file is well-formed but provenance and audit-trail are lost; "
        "produced by writers that do not capture user identity or origin and emit empty strings; "
        "expected kernel behavior: heal and accept — parse normally; "
        "on re-emit, normalize by populating at least originating_system with the kernel's identity; "
        "synonyms: STEP has no author, can't tell who created this STEP, lost provenance, "
        "STEP file no provenance, empty FILE_NAME author field"
    ),
)


def _render_wr028() -> str:
    """Render a Part-21 with blank FILE_NAME provenance fields."""
    return (
        "ISO-10303-21;\n"
        "/* Wr028: FILE_NAME.author and originating_system fields blank */\n"
        "/* All provenance fields are empty strings: author, organization, */\n"
        "/* originating_system, and authorisation are all '' */\n"
        "/* Produced by writers that do not capture user identity or origin */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr028'),'2;1');\n"
        "/* DEFECT: author=(''), organization=(''), originating_system='', authorisation='' */\n"
        "FILE_NAME('Wr028.stp','2026-06-17T00:00:00',(''),(''),'','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: minimal GEOMETRIC_CURVE_SET — defect is in HEADER only */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('pt',(1.,0.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('no-provenance-shape',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr028(path) -> None:
    Path(path).write_text(_render_wr028())


f.render = _render_wr028  # type: ignore[method-assign]
f.write = _write_wr028    # type: ignore[method-assign]
