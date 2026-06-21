"""U045 — `CARTESIAN_TRANSFORMATION_OPERATOR` `scale` attribute parsed but never applied (BRL-CAD step-g).

Catalog claim: BRL-CAD step-g's Load pass parses the optional scale REAL attribute into a class
member, but LoadONBrep is an unconditional stub that prints "::LoadONBrep(..) not implemented for
<entity>" — the scale never reaches the resulting ON_Xform. A producer's intent to scale a
sub-component (e.g. inch-prototype scaled to mm by scale=25.4) is silently lost; the located
sub-shape arrives at unit scale.

Reproducer recipe: CARTESIAN_TRANSFORMATION_OPERATOR_3D('inch_to_mm', ..., 25.4, ...)
referenced as a transformation between two representations. step-g loads but does not apply scale.

Byte assertions:
  contains(b'CARTESIAN_TRANSFORMATION_OPERATOR_3D')
  contains(b'25.4')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U045",
    defect=(
        "CARTESIAN_TRANSFORMATION_OPERATOR_3D scale attribute parsed but never applied "
        "(BRL-CAD step-g LoadONBrep stub); "
        "input: STEP file with CARTESIAN_TRANSFORMATION_OPERATOR_3D whose scale=25.4 "
        "is intended to convert a 1-inch prototype into 25.4 mm; "
        "BRL-CAD step-g Load() reads the optional scale REAL into a class member, "
        "but LoadONBrep() is an unconditional stub printing "
        "'::LoadONBrep(..) not implemented for CARTESIAN_TRANSFORMATION_OPERATOR_3D'; "
        "the scale never reaches the resulting ON_Xform or gp_Trsf; "
        "producer intent — place this prototype at this location and scale by 25.4 — is silently lost; "
        "the 1-unit prototype arrives at unit scale (1 mm) instead of the intended 25.4 mm; "
        "symmetric reader-side defect to U015/Wr050 (writer composes scale twice); "
        "kernel must implement LoadONBrep for CARTESIAN_TRANSFORMATION_OPERATOR_3D "
        "and build a uniform-scale ON_Xform from the parsed scale value; "
        "emit W_OPERATOR_SCALE_APPLIED diagnostic recording the factor; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: CartesianTransformationOperator scale parsed but ignored, "
        "STEP scale operator does nothing on import, "
        "step-g LoadONBrep stub for transformation operator, "
        "uniform scale 25.4 dropped by reader, "
        "BRL-CAD subassembly arrives unit scale despite operator scale"
    ),
)


def _render_u045() -> str:
    """Render a Part-21 with CARTESIAN_TRANSFORMATION_OPERATOR_3D using scale=25.4."""
    return (
        "ISO-10303-21;\n"
        "/* U045: CARTESIAN_TRANSFORMATION_OPERATOR_3D scale=25.4 (inch->mm conversion) */\n"
        "/* DEFECT (BRL-CAD step-g): LoadONBrep stub silently drops the scale attribute */\n"
        "/* Producer intent: place 1-unit inch prototype scaled by 25.4 to get 25.4 mm part */\n"
        "/* Buggy receiver (step-g): stub ignores scale; subassembly arrives at 1 mm (unit scale) */\n"
        "/* Correct receiver: build uniform-scale xform from parsed scale=25.4 */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U045: CARTESIAN_TRANSFORMATION_OPERATOR_3D scale=25.4 ignored by step-g'),'2;1');\n"
        "FILE_NAME('U045.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Standard mm context for assembly */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Prototype geometry: 1-unit (inch) coordinates — should become 25.4 mm after scaling */\n"
        "#1=CARTESIAN_POINT('proto_origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('proto_corner_a',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('proto_corner_b',(0.,1.,0.));\n"
        "#4=CARTESIAN_POINT('proto_corner_c',(1.,1.,1.));\n"
        "/* Prototype representation (inch-space) */\n"
        "#20=GEOMETRIC_CURVE_SET('inch_prototype',(#1,#2,#3,#4));\n"
        "#21=SHAPE_REPRESENTATION('inch_proto_rep',(#20),#14);\n"
        "/* Assembly-space axes for the CARTESIAN_TRANSFORMATION_OPERATOR_3D */\n"
        "#30=CARTESIAN_POINT('xform_origin',(0.,0.,0.));\n"
        "#31=DIRECTION('xform_axis1',(0.,0.,1.));\n"
        "#32=DIRECTION('xform_axis2',(1.,0.,0.));\n"
        "#33=CARTESIAN_POINT('xform_local_origin',(0.,0.,0.));\n"
        "#34=DIRECTION('xform_local_axis1',(0.,0.,1.));\n"
        "#35=DIRECTION('xform_local_axis2',(1.,0.,0.));\n"
        "/* CARTESIAN_TRANSFORMATION_OPERATOR_3D: inch->mm scale factor = 25.4 */\n"
        "/* BRL-CAD step-g Load() reads scale=25.4 into member variable */\n"
        "/* BRL-CAD step-g LoadONBrep() is a stub: scale is NEVER applied */\n"
        "#100=CARTESIAN_TRANSFORMATION_OPERATOR_3D('inch_to_mm',#30,#31,#32,25.4,#33,#34,#35);\n"
        "/* Assembly representation referencing the transformation */\n"
        "#110=SHAPE_REPRESENTATION('assembly_rep',(#20),#14);\n"
        "/* REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION links the two representations */\n"
        "#120=REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(\n"
        "  'inch_to_mm_placement','scale 25.4 inch to mm',#21,#110,#100);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#200=GEOMETRIC_CURVE_SET('cartesian-transform-scale-dropped',(#1,#2,#3,#4));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u045(path) -> None:
    Path(path).write_text(_render_u045())


f.render = _render_u045  # type: ignore[method-assign]
f.write = _write_u045    # type: ignore[method-assign]
