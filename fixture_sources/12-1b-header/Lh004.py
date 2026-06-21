"""Lh004 — HEADER section missing one of the three required entities (FILE_SCHEMA omitted).

Catalog claim: ISO 10303-21 requires exactly one each of FILE_DESCRIPTION, FILE_NAME,
FILE_SCHEMA, in that order. This fixture omits FILE_SCHEMA entirely. Bug-reporter
language: "FILE_SCHEMA missing from HEADER", "DATA before HEADER in STEP",
"header records out of order", "duplicated header entity".

Reproducer recipe: HEADER; FILE_NAME('a.stp','..',(''),(''),'','','');
FILE_DESCRIPTION((''),'2;1'); ENDSEC; (no FILE_SCHEMA).

Byte assertions:
  not matches(rb'FILE_SCHEMA\\s*\\(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=reject
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh004",
    defect=(
        "HEADER section missing FILE_SCHEMA (one of the three required header entities); "
        "input: HEADER section contains FILE_DESCRIPTION and FILE_NAME but no FILE_SCHEMA; "
        "ISO 10303-21 §8 requires exactly one each of FILE_DESCRIPTION, FILE_NAME, FILE_SCHEMA "
        "in that order; omitting FILE_SCHEMA leaves the receiver without a schema binding and "
        "forces it to guess (or null-deref the schema pointer and crash); "
        "produced by hand-edited files, minimalist exporters, or partially-generated files "
        "where the schema record is accidentally dropped; "
        "expected kernel behavior: reject with 'missing required header entity FILE_SCHEMA'; "
        "never null-deref the schema pointer; "
        "see also: Lh005; "
        "synonyms: FILE_SCHEMA missing from HEADER, header incomplete, no schema in STEP file, "
        "FILE_NAME twice in HEADER, DATA before HEADER in STEP, header records out of order"
    ),
)


def _render_lh004() -> str:
    """Render a Part-21 with the schema header record omitted from the HEADER section."""
    return (
        "ISO-10303-21;\n"
        "/* Lh004: HEADER section missing required schema record */\n"
        "/* ISO 10303-21 §8: HEADER must contain exactly one each of: */\n"
        "/*   FILE_DESCRIPTION, FILE_NAME, and the schema declaration — in that order */\n"
        "/* DEFECT: schema header record is absent; receiver has no schema binding */\n"
        "/* Minimalist exporters and hand-edited files drop this record */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh004: schema record missing from HEADER section'),'2;1');\n"
        "FILE_NAME('Lh004.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: schema declaration record intentionally absent — ENDSEC follows immediately */\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('missing-schema-record-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh004(path) -> None:
    Path(path).write_text(_render_lh004())


f.render = _render_lh004  # type: ignore[method-assign]
f.write = _write_lh004    # type: ignore[method-assign]
