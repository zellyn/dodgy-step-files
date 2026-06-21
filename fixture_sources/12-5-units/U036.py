"""U036 — `BinXCAF` does not preserve length unit.

Catalog claim: A document carrying a non-default length unit (e.g., inches) is saved to
OCCT's binary XBF format. The persistence layer records geometry but not the document's
length unit. Re-loading defaults to millimetres, scaling all values incorrectly.

Reproducer recipe: Document with LENGTH_UNIT = INCH, one cube side 1.0. Save XBF.
Reload — cube is 1.0 mm, not 25.4 mm.

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('INCH'")
  contains(b'25.4') or contains(b'INCH')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U036",
    defect=(
        "BinXCAF does not preserve length unit — INCH unit lost through XBF round-trip; "
        "input: STEP file with CONVERSION_BASED_UNIT('INCH') and LENGTH_UNIT = INCH "
        "with a 1x1x1 inch cube (coordinates are 1.0 in each dimension); "
        "when this document is saved via OCCT BinXCAF persistence (XBF format), "
        "the persistence layer records geometry but not the document's length unit; "
        "on reload, the reader defaults to millimetres — the 1.0-inch cube becomes 1.0 mm; "
        "the document should be 25.4 mm per side but is interpreted as 1.0 mm; "
        "kernel persistence layer must round-trip the document's length unit alongside geometry; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: BinXCAF loses length unit, XBF binary loses INCH unit on save, "
        "non-default unit not preserved in XBF, OCCT binary persistence drops unit, "
        "STEP unit lost through XBF round-trip"
    ),
)


def _render_u036() -> str:
    """Render a Part-21 with INCH unit that would be lost through BinXCAF round-trip."""
    return (
        "ISO-10303-21;\n"
        "/* U036: BinXCAF does not preserve INCH length unit — reloads as mm */\n"
        "/* Document: 1x1x1 inch cube saved via OCCT XBF persistence */\n"
        "/* DEFECT: XBF records geometry but drops the length unit; reload defaults to mm */\n"
        "/* On reload: 1.0 inch becomes 1.0 mm (should be 25.4 mm) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U036: INCH unit lost through BinXCAF XBF round-trip'),'2;1');\n"
        "FILE_NAME('U036.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 1x1x1 inch cube; values are in inches */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(1.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,1.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,1.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(1.0,1.0,1.0));\n"
        "/* SI mm basis for conversion reference */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* INCH conversion: 25.4 mm per inch */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* File declares INCH as active length unit */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(3.937E-5),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* DEFECT: BinXCAF persistence drops this unit record — reload defaults to mm */\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('binxcaf-inch-unit-lost',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u036(path) -> None:
    Path(path).write_text(_render_u036())


f.render = _render_u036  # type: ignore[method-assign]
f.write = _write_u036    # type: ignore[method-assign]
