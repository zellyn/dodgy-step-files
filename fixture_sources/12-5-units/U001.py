"""U001 — Solid Edge mm exported STEP read as meters by Inventor (1000x too big).

Catalog claim: STEP written from Solid Edge with LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.)
plus coordinates in mm (100x50 mm extents) is interpreted by Inventor as base SI (metre),
giving an imported part 1000 times bigger than expected. The receiver ignores the producer's
LENGTH_UNIT context and defaults to base SI.

Reproducer recipe: GEOMETRIC_REPRESENTATION_CONTEXT whose units list contains
(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI., .METRE.)); coordinates encoded as raw mm;
reader strips the prefix and treats the number as metres.

Byte assertions:
  contains(b'SI_UNIT(.MILLI.,.METRE.)') or contains(b'SI_UNIT(.MILLI., .METRE.)')
  matches(rb'GEOMETRIC_REPRESENTATION_CONTEXT|REPRESENTATION_CONTEXT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U001",
    defect=(
        "Solid Edge mm STEP read as metres by Inventor (1000x too big); "
        "input: STEP file produced by Solid Edge with LENGTH_UNIT SI_UNIT(.MILLI.,.METRE.) "
        "and coordinates encoded as raw millimetre values (100.0, 50.0, 25.0); "
        "Inventor legacy importer strips the MILLI prefix and treats the numeric values as "
        "base SI metres, loading a part 1000 times larger than intended; "
        "the receiver ignores the producer's LENGTH_UNIT context "
        "(and any auxiliary DIMENSIONAL_EXPONENTS instance) and defaults to base SI; "
        "kernel must honour SI_UNIT.prefix and never silently rescale because the reader "
        "expected another unit; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: Solid Edge mm imported as meters 1000x bigger, Inventor reads STEP mm as metres, "
        "STEP imported 1000 times too large, mm prefix ignored on STEP import, "
        "MILLI METRE silently treated as METRE"
    ),
)


def _render_u001() -> str:
    """Render a Part-21 with SI_UNIT(.MILLI.,.METRE.) and mm-scale coordinates."""
    return (
        "ISO-10303-21;\n"
        "/* U001: Solid Edge mm STEP read as metres by Inventor (1000x too big) */\n"
        "/* Solid Edge emits LENGTH_UNIT with SI_UNIT(.MILLI.,.METRE.) and mm coordinates */\n"
        "/* Inventor legacy importer strips .MILLI. prefix and reads values as base metres */\n"
        "/* Result: a 100x50 mm part loads at 100x50 m — 1000x too large */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U001: SI_UNIT(.MILLI.,.METRE.) prefix ignored on STEP import'),'2;1');\n"
        "FILE_NAME('U001.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: a 100x50x25 mm box expressed in millimetre coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(100.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(100.0,50.0,25.0));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: SI_UNIT with .MILLI. prefix — Inventor treats numeric values as metres */\n"
        "/* not millimetres; a coordinate of 100.0 should be 0.1 m after unit application */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "/* UNCERTAINTY_MEASURE_WITH_UNIT at 0.001 mm (typical Solid Edge signature) */\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('solid-edge-mm-part',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u001(path) -> None:
    Path(path).write_text(_render_u001())


f.render = _render_u001  # type: ignore[method-assign]
f.write = _write_u001    # type: ignore[method-assign]
