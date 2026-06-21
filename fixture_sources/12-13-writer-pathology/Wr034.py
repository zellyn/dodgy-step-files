"""Wr034 — Coordinate-system axis swap without notification (Y-up vs Z-up).

Catalog claim: geometry coordinates were authored in a Y-up coordinate system (web-CAD /
game-engine convention), but the writer emitted them as-is without applying the rotation
that makes Z the up-axis (STEP/CAD convention). Receiver loads the geometry rotated 90°
around X. Bug-reporter language: "model lying on its side", "Y-up vs Z-up",
"STEP imported sideways", "coordinate axes swapped".

Reproducer recipe: a GEOMETRIC_CURVE_SET / MANIFOLD_SOLID_BREP whose vertices imply
vertical extent along Y rather than Z, with a comment noting input was authored Y-up
and emitted without rotation.

Byte assertions:
  contains(b'Y-up') or contains(b'Z-up')
  contains(b'Y-up')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr034",
    defect=(
        "coordinate-system axis swap without notification (Y-up vs Z-up); "
        "input: geometry authored in Y-up coordinate system (web-CAD/game-engine convention); "
        "writer emitted coordinates as-is without applying the rotation to make Z the up-axis "
        "(STEP/CAD convention); receiver loads geometry rotated 90 degrees around X-axis; "
        "produced by web-CAD and game-engine-derived writers whose internal convention is Y-up; "
        "they export to STEP without applying the Z-up coordinate transform; "
        "expected kernel behavior: warn and accept — normalize by trusting the DATA-section "
        "AXIS2_PLACEMENT_3D coordinate system; if the application expects Z-up, "
        "emit a 'model appears Y-up' diagnostic when the geometry bounding box has "
        "inverted aspect ratio; "
        "synonyms: model lying on its side, Y-up vs Z-up, STEP imported sideways, "
        "coordinate axes swapped, STEP imported on its side"
    ),
)


def _render_wr034() -> str:
    """Render a Part-21 representing Y-up authored geometry emitted without Z-up transform."""
    return (
        "ISO-10303-21;\n"
        "/* Wr034: coordinate-system axis swap without notification (Y-up vs Z-up) */\n"
        "/* Input was authored in a Y-up coordinate system (web-CAD/game-engine convention) */\n"
        "/* Writer emitted coordinates as-is; did not apply the Y-up to Z-up rotation */\n"
        "/* STEP/CAD convention: Z is up; this file has geometry with vertical extent along Y */\n"
        "/* Receivers that assume Z-up load the model rotated 90 degrees on its side */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr034: Y-up geometry emitted without Z-up transform'),'2;1');\n"
        "FILE_NAME('Wr034.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: geometry vertices have largest extent in Y-axis (Y-up authoring) */\n"
        "/* Correct Z-up STEP file would have largest extent in Z; writer skipped the transform */\n"
        "/* Y-up source had a tall tower: base at Y=0, apex at Y=10; emitted without rotation */\n"
        "#1=CARTESIAN_POINT('base-corner-0',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('base-corner-1',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('base-corner-2',(1.,0.,1.));\n"
        "#4=CARTESIAN_POINT('base-corner-3',(0.,0.,1.));\n"
        "#5=CARTESIAN_POINT('apex-corner-0',(0.,10.,0.));\n"
        "#6=CARTESIAN_POINT('apex-corner-1',(1.,10.,0.));\n"
        "#7=CARTESIAN_POINT('apex-corner-2',(1.,10.,1.));\n"
        "#8=CARTESIAN_POINT('apex-corner-3',(0.,10.,1.));\n"
        "#9=GEOMETRIC_CURVE_SET('Y-up-authored-tower-shape',(#1,#2,#3,#4,#5,#6,#7,#8));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr034(path) -> None:
    Path(path).write_text(_render_wr034())


f.render = _render_wr034  # type: ignore[method-assign]
f.write = _write_wr034    # type: ignore[method-assign]
