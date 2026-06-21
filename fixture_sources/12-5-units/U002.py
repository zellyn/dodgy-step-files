"""U002 — Onshape always emits METRE; NX rescales as if mm (1000x too small).

Catalog claim: Onshape always emits length unit .METRE. regardless of workspace display
unit. NX accepts only inch or millimetre and silently treats metric STEP as mm, yielding
a 1000x too-small body.

Reproducer recipe: SI_UNIT($, .METRE.) (no prefix) with coordinate magnitudes appropriate
for metres; consume in NX configured for mm.

Byte assertions:
  matches(rb'SI_UNIT\\(\\$\\s*,\\s*\\.METRE\\.\\)')
  count(b'.METRE.') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U002",
    defect=(
        "Onshape always emits METRE; NX rescales as if mm (1000x too small); "
        "input: STEP file produced by Onshape with SI_UNIT($,.METRE.) regardless of workspace "
        "display unit setting; coordinates are in metre-scale values (e.g. 0.1, 0.05) "
        "appropriate for a 100x50 mm part expressed in metres; "
        "NX accepts only inch or millimetre and silently treats the metric STEP as mm, "
        "scaling a 0.1-metre value as if it were 0.1 mm — 1000x too small; "
        "kernel must read the declared length unit verbatim and never assume; "
        "if the display unit differs, normalize/scale internally; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: Onshape STEP comes in 1000x too small in NX, Onshape always emits METRE, "
        "NX reads metres as mm, STEP metres misread as mm, metric STEP 1000x smaller in NX"
    ),
)


def _render_u002() -> str:
    """Render a Part-21 with SI_UNIT($,.METRE.) and metre-scale coordinates."""
    return (
        "ISO-10303-21;\n"
        "/* U002: Onshape always emits METRE; NX treats metric STEP as mm (1000x too small) */\n"
        "/* Onshape writes SI_UNIT($,.METRE.) with no prefix regardless of workspace display unit */\n"
        "/* Coordinates are in metres: a 100x50 mm part appears as 0.1 x 0.05 m */\n"
        "/* NX silently reads metre values as mm => body is 1000x too small */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U002: SI_UNIT(METRE) from Onshape misread as mm by NX'),'2;1');\n"
        "FILE_NAME('U002.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 100x50 mm part authored in Onshape, exported in metre coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(0.1,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,0.05,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,0.025));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(0.1,0.05,0.025));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: SI_UNIT($,.METRE.) — no MILLI prefix — Onshape always writes base metre */\n"
        "/* NX configured for mm silently treats 0.1 m as 0.1 mm => 1000x too small */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('onshape-metre-part',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u002(path) -> None:
    Path(path).write_text(_render_u002())


f.render = _render_u002  # type: ignore[method-assign]
f.write = _write_u002    # type: ignore[method-assign]
