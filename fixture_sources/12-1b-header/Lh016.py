"""Lh016 — Edition-3 extra header entities (FILE_INFO, FILE_POPULATION, SECTION_LANGUAGE, …).

Catalog claim: Edition 3 allows additional header entities beyond the required three
(FILE_POPULATION, SECTION_LANGUAGE, implementation-private entries). Strict Edition-1/2
readers reject any header entity beyond the canonical three; tolerant Edition-3 readers
must accept them.
Bug-reporter language: "FILE_POPULATION header record", "Edition 3 extra header entities",
"SECTION_LANGUAGE in HEADER", "Ed.2 reader rejects FILE_INFO",
"Edition 3 header beyond required three".

Reproducer recipe: append FILE_INFO('Report Date','2025-04-21 18:16:37', ..);
  between FILE_SCHEMA and ENDSEC.

Byte assertions:
  contains(b'FILE_POPULATION') or contains(b'SECTION_LANGUAGE') or contains(b'FILE_INFO')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh016",
    defect=(
        "Edition-3 extra header entities in HEADER section rejected by strict Ed.1/2 readers; "
        "input: HEADER section contains FILE_INFO and FILE_POPULATION after the required "
        "three entities (FILE_DESCRIPTION, FILE_NAME, FILE_SCHEMA); "
        "ISO 10303-21 Edition 3 permits additional entities such as FILE_POPULATION, "
        "SECTION_LANGUAGE, and implementation-private entries; "
        "strict Edition-1/2 readers reject any HEADER entity beyond the canonical three; "
        "tolerant Edition-3 readers must accept them; "
        "produced by Edition-3-aware exporters writing files intended for mixed-edition deployments; "
        "expected kernel behavior: accept any number of extra header entities under Edition 3; "
        "warn for unknown names; reject under strict Edition-2 mode; "
        "synonyms: FILE_POPULATION header record, Edition 3 extra header entities, "
        "SECTION_LANGUAGE in HEADER, Ed.2 reader rejects FILE_INFO, "
        "Edition 3 header beyond required three"
    ),
)


def _render_lh016() -> str:
    """Render a Part-21 with Edition-3 extra header entities (FILE_INFO, FILE_POPULATION)."""
    return (
        "ISO-10303-21;\n"
        "/* Lh016: Edition-3 extra header entities beyond the required three */\n"
        "/* ISO 10303-21 Ed.3: FILE_POPULATION, SECTION_LANGUAGE, FILE_INFO are permitted */\n"
        "/* Strict Ed.1/2 readers reject any header entity beyond the canonical three */\n"
        "/* DEFECT: FILE_INFO and FILE_POPULATION appear after FILE_SCHEMA */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh016: Edition-3 extra header entities FILE_INFO FILE_POPULATION'),'2;1');\n"
        "FILE_NAME('Lh016.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "/* DEFECT: Ed.3 extensions — strict Ed.1/2 readers reject these additional records */\n"
        "FILE_INFO('Report Date','2025-04-21 18:16:37','');\n"
        "FILE_POPULATION('default',(''),(#5));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('ed3-extra-header-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh016(path) -> None:
    Path(path).write_text(_render_lh016())


f.render = _render_lh016  # type: ignore[method-assign]
f.write = _write_lh016    # type: ignore[method-assign]
