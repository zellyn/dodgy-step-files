"""Wr018 — Empty SHAPE_DEFINITION_REPRESENTATION chain (placeholder with no geometry).

Catalog claim: complete product-structure scaffold with APPLICATION_CONTEXT,
PRODUCT, PRODUCT_DEFINITION, SHAPE_DEFINITION_REPRESENTATION, and
SHAPE_REPRESENTATION, but SHAPE_REPRESENTATION.items contains only an
AXIS2_PLACEMENT_3D; no MANIFOLD_SOLID_BREP, no geometry.

Reproducer recipe: full scaffold ending with
SHAPE_REPRESENTATION('main',(#13),#24) where #13 is just an
AXIS2_PLACEMENT_3D and there is no shape.

Byte assertions:
  matches(rb"SHAPE_REPRESENTATION\('[^']*',\(#\d+\),#")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr018",
    defect=(
        "Empty SHAPE_DEFINITION_REPRESENTATION chain (placeholder structure with no geometry); "
        "writer initialises product structure tree before geometry is computed; "
        "forgets to suppress empty trees on export when computation fails or is cancelled; "
        "file contains complete product scaffold with APPLICATION_CONTEXT, PRODUCT, "
        "PRODUCT_DEFINITION, SHAPE_DEFINITION_REPRESENTATION, SHAPE_REPRESENTATION; "
        "but SHAPE_REPRESENTATION.items list contains only an AXIS2_PLACEMENT_3D; "
        "no MANIFOLD_SOLID_BREP, no SHELL_BASED_SURFACE_MODEL, no tessellation; "
        "receiver loads successfully but reports zero solids; "
        "expected kernel behavior: warn and accept; "
        "emit a warning that the file describes a product but contains no geometry; "
        "do not reject (well-formed empty product is permitted); "
        "synonyms: STEP file loaded but nothing visible, empty model, "
        "product tree but no geometry, ghost STEP file"
    ),
)


def _render_wr018() -> str:
    """Render a Part-21 with a complete product scaffold but no geometry items."""
    return (
        "ISO-10303-21;\n"
        "/* Wr018: complete product scaffold with no geometry in SHAPE_REPRESENTATION */\n"
        "/* Writer initialised product structure before geometry was computed */\n"
        "/* SHAPE_REPRESENTATION.items contains only an AXIS2_PLACEMENT_3D */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr018 - empty shape representation chain'),'2;1');\n"
        "FILE_NAME('Wr018.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Product structure scaffold */\n"
        "#1=APPLICATION_CONTEXT('mechanical design');\n"
        "#2=APPLICATION_PROTOCOL_DEFINITION('international standard',\n"
        "  'automotive_design',2003,#1);\n"
        "#3=PRODUCT_CONTEXT('',#1,'mechanical');\n"
        "#4=PRODUCT('Wr018','Wr018','',(#3));\n"
        "#5=PRODUCT_DEFINITION_FORMATION('','',#4);\n"
        "#6=PRODUCT_DEFINITION_CONTEXT(#1,'design');\n"
        "#7=PRODUCT_DEFINITION('design','',#5,#6);\n"
        "#8=PRODUCT_DEFINITION_SHAPE('','',#7);\n"
        "/* Placement axis — this is the ONLY item in SHAPE_REPRESENTATION */\n"
        "#9=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#10=DIRECTION('z-axis',(0.,0.,1.));\n"
        "#11=DIRECTION('x-axis',(1.,0.,0.));\n"
        "#12=AXIS2_PLACEMENT_3D('placement',#9,#10,#11);\n"
        "/* Unit context */\n"
        "#13=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#14=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#15=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "#16=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#13,\n"
        "  'distance_accuracy_value','');\n"
        "#17=(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
        "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#16))"
        "GLOBAL_UNIT_ASSIGNED_CONTEXT((#13,#14,#15))"
        "REPRESENTATION_CONTEXT('','3D'));\n"
        "/* SHAPE_REPRESENTATION with only a placement — no geometry shape */\n"
        "#18=SHAPE_REPRESENTATION('main',(#12),#17);\n"
        "#19=SHAPE_DEFINITION_REPRESENTATION(#8,#18);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr018(path) -> None:
    Path(path).write_text(_render_wr018())


f.render = _render_wr018  # type: ignore[method-assign]
f.write = _write_wr018    # type: ignore[method-assign]
