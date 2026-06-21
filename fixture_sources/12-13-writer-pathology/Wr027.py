"""Wr027 — Unit context emitted twice with different units (HEADER vs DATA mismatch).

Catalog claim: FILE_DESCRIPTION (or FILE_NAME description string) says 'part in mm'
while the DATA-section LENGTH_UNIT resolves to INCH. Geometry is correct in DATA-section
units (INCH); the HEADER prose is misleading. Bug-reporter language: "header says mm,
geometry is inches", "STEP file has two different units".

Reproducer recipe: FILE_DESCRIPTION(('part in mm'),'2;1') paired with a LENGTH_UNIT
resolving to INCH in the DATA section.

Byte assertions:
  contains(b"'INCH'") and contains(b"part in mm")
  contains(b"'INCH'")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr027",
    defect=(
        "unit context emitted twice with different units (HEADER vs DATA mismatch); "
        "input: FILE_DESCRIPTION prose claims 'part in mm' while DATA-section LENGTH_UNIT "
        "resolves to INCH via CONVERSION_BASED_UNIT; "
        "geometry is correct in DATA-section INCH units; "
        "HEADER description string is decorative but misleading; "
        "produced by writers where HEADER is composed by a templating subsystem "
        "and DATA-section unit context is emitted by a separate geometry serialiser "
        "with no cross-check between them; "
        "expected kernel behavior: warn and accept — normalize by trusting the DATA-section "
        "unit context (the schema-meaningful one) and treat HEADER prose as informational; "
        "emit a warning on unit mismatch between HEADER and DATA; "
        "synonyms: header says mm geometry is inches, STEP file has two different units, "
        "unit declaration contradicts geometry"
    ),
)


def _render_wr027() -> str:
    """Render a Part-21 with header/DATA unit mismatch."""
    return (
        "ISO-10303-21;\n"
        "/* Wr027: unit context emitted twice with different units (HEADER vs DATA mismatch) */\n"
        "/* HEADER description prose claims 'part in mm'; DATA-section LENGTH_UNIT is INCH */\n"
        "/* Geometry is correct at DATA-section (INCH) scale; the HEADER string is decorative */\n"
        "/* Produced by writers with separate HEADER-templating and geometry-serialisation subsystems */\n"
        "HEADER;\n"
        "/* DEFECT: FILE_DESCRIPTION says 'part in mm' but DATA section uses INCH */\n"
        "FILE_DESCRIPTION(('part in mm'),'2;1');\n"
        "FILE_NAME('Wr027.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: a 1-inch unit cube edge expressed in INCH-scale coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('inch-geometry',());\n"
        "/* DEFECT: LENGTH_UNIT resolves to INCH, contradicting the HEADER 'part in mm' claim */\n"
        "#10=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#20);\n"
        "#20=(LENGTH_UNIT()NAMED_UNIT(*)CONVERSION_BASED_UNIT('INCH',#21));\n"
        "#21=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#22=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#23=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr027(path) -> None:
    Path(path).write_text(_render_wr027())


f.render = _render_wr027  # type: ignore[method-assign]
f.write = _write_wr027    # type: ignore[method-assign]
