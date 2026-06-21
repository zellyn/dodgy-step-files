"""Wr035 — Coordinate scale-factor applied twice (model 1000× larger or smaller than expected).

Catalog claim: numeric coordinates are 1000× too large because the writer applied the
m-to-mm factor in both the coordinate transform *and* the unit declaration. A model
authored as a 1.0-metre cube has coordinates emitted as (1000.0, 1000.0, 1000.0) while
LENGTH_UNIT is declared as MILLI METRE; receivers apply the mm scale a second time and
see the model at 1000× its intended size. Bug-reporter language: "model 1000× too small
after import", "STEP file scaled by 1000", "tiny model", "huge model",
"millimetre-vs-metre mistake".

Reproducer recipe: a CARTESIAN_POINT at (1000.0, 1000.0, 1000.0) with LENGTH_UNIT
declared as MILLI METRE, comment noting input was a 1.0-metre cube.

Byte assertions:
  matches(rb'CARTESIAN_POINT\\([^;]*1000(?:\\.0)?,1000') or contains(b'1000.0,1000.0,1000.0')
  matches(rb'1000') and contains(b'.MILLI.')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr035",
    defect=(
        "coordinate scale-factor applied twice (model 1000x larger or smaller than expected); "
        "input: model authored in metres as a 1.0-metre cube; "
        "writer applied m-to-mm factor (×1000) to coordinates AND declared LENGTH_UNIT as MILLI METRE; "
        "receiver applies the declared mm factor a second time and sees the model 1000× too large; "
        "CARTESIAN_POINT emitted as (1000.0,1000.0,1000.0) but unit declaration says coordinates "
        "are already in millimetres — so receiver multiplies again; "
        "produced by writers with bugs in unit-conversion pipeline that scale coordinates "
        "and then also declare the scaled unit without clearing the coordinate transform; "
        "expected kernel behavior: heal and accept — normalize by trusting the DATA-section "
        "unit declaration; warn if bounding box exceeds plausible bounds for declared unit; "
        "synonyms: model 1000x too small after import, STEP file scaled by 1000, tiny model, "
        "huge model, millimetre-vs-metre mistake, double unit conversion"
    ),
)


def _render_wr035() -> str:
    """Render a Part-21 where m-to-mm scale was applied twice."""
    return (
        "ISO-10303-21;\n"
        "/* Wr035: coordinate scale-factor applied twice (model 1000x too large) */\n"
        "/* Input was a 1.0-metre cube; writer applied m-to-mm (x1000) to coordinates */\n"
        "/* AND declared LENGTH_UNIT as MILLI METRE — receiver applies factor a second time */\n"
        "/* Result: receiver sees a cube 1000x larger than the producer intended */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr035: double unit-conversion scale defect'),'2;1');\n"
        "FILE_NAME('Wr035.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: coordinates are 1000.0 (already mm-scaled), but unit says MILLI METRE */\n"
        "/* A 1.0-metre cube should have corners at (1000.0,...) in mm — but unit declaration */\n"
        "/* already tells receiver these are mm values; receiver multiplies again => 1e6 mm */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-xxx',(1000.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-xxy',(1000.0,1000.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-xyy',(0.,1000.0,0.));\n"
        "#5=CARTESIAN_POINT('corner-xxz',(1000.0,0.,1000.0));\n"
        "#6=CARTESIAN_POINT('corner-xyz',(1000.0,1000.0,1000.0));\n"
        "#7=DIRECTION('xdir',(1.,0.,0.));\n"
        "#8=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: unit declared as MILLI METRE while coordinates already reflect mm-scaling */\n"
        "#9=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#10=GEOMETRIC_CURVE_SET('double-scaled-1m-cube',(#1,#2,#3,#4,#5,#6));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr035(path) -> None:
    Path(path).write_text(_render_wr035())


f.render = _render_wr035  # type: ignore[method-assign]
f.write = _write_wr035    # type: ignore[method-assign]
