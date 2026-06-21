"""U043 — Slicer-side unit-context inversion: STEP says inch, slicer reads as mm.

Catalog claim: A producer-side STEP correctly declares INCH units with inch-scale numerical
values. A receiver that hard-codes 'STEP files are mm' silently treats the inch values as mm,
yielding a 25.4x too-small model. The on-disk file is well-formed; the bug is that some slicer
lineage assumes mm regardless of the declared unit context.

Reproducer recipe: STEP file with LENGTH_UNIT complex record
(LENGTH_UNIT() NAMED_UNIT(*) CONVERSION_BASED_UNIT('INCH', ..)) and CARTESIAN_POINT corner
coordinates (1.0, 1.0, 1.0) (one inch — should appear as 25.4 mm to a correct receiver).

Byte assertions:
  contains(b'INCH')
  contains(b'CONVERSION_BASED_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U043",
    defect=(
        "Slicer-side unit-context inversion: STEP declares INCH but receiver hard-codes mm; "
        "input: well-formed STEP file with LENGTH_UNIT declared as INCH via "
        "( CONVERSION_BASED_UNIT('INCH',#ref25_4mm) LENGTH_UNIT() NAMED_UNIT(*) ) "
        "where #ref25_4mm = LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#mm_base) "
        "and CARTESIAN_POINT corner coordinates are (1.0,1.0,1.0) — one inch per side; "
        "a correct receiver normalises the INCH context and loads a 25.4 mm cube; "
        "a buggy receiver (slicer lineage) hard-codes the assumption that all STEP coordinates "
        "are in millimetres and ignores the CONVERSION_BASED_UNIT declaration; "
        "result: the 1.0-inch values are treated as 1.0 mm, yielding a model 25.4x too small; "
        "mirror image of Wr044 (writer side); "
        "kernel must honour the declared LENGTH_UNIT context and normalise coordinate values "
        "into the kernel's canonical unit; "
        "reject with E_UNIT_CONTEXT_IGNORED if the unit declaration cannot be parsed; "
        "never assume mm without inspecting the declared context; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: slicer ignores STEP unit declaration, INCH unit silently treated as mm, "
        "unit-context inversion on receiver side, 25.4x model too small from slicer, "
        "STEP INCH declaration ignored, receiver hard-codes mm assumption"
    ),
)


def _render_u043() -> str:
    """Render a well-formed Part-21 with INCH unit; 1x1x1 inch cube (coords = 1.0 each side)."""
    return (
        "ISO-10303-21;\n"
        "/* U043: Well-formed STEP with INCH unit; 1x1x1 inch cube */\n"
        "/* DEFECT (receiver side): slicer ignores CONVERSION_BASED_UNIT('INCH') declaration */\n"
        "/* Correct receiver: loads 25.4 mm cube */\n"
        "/* Buggy receiver (hard-codes mm): loads 1.0 mm cube (25.4x too small) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U043: INCH unit declared; receiver must honour, not hard-code mm'),'2;1');\n"
        "FILE_NAME('U043.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* SI mm base — required as the conversion reference for INCH */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* INCH conversion: exactly 25.4 mm per inch */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* File declares INCH as active length unit */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(3.937E-5),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Geometry: 1x1x1 inch cube (corner coords at 1.0 — one inch per side) */\n"
        "/* Correct receiver: normalises to 25.4 mm per side */\n"
        "/* Buggy receiver (hard-codes mm): reads as 1.0 mm per side (25.4x too small) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(1.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,1.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,1.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(1.0,1.0,1.0));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#30=GEOMETRIC_CURVE_SET('inch-unit-receiver-ignores-declaration',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u043(path) -> None:
    Path(path).write_text(_render_u043())


f.render = _render_u043  # type: ignore[method-assign]
f.write = _write_u043    # type: ignore[method-assign]
