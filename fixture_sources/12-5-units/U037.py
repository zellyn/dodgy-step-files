"""U037 — `RescaleGeometry` does not rescale triangulations.

Catalog claim: A part with both B-rep and triangulated representation is rescaled
(e.g., from inches to millimetres). The rescale operates on the B-rep but skips the
attached triangulation, producing a part whose mesh is at the wrong scale.

Reproducer recipe: Cube with LENGTH_UNIT = INCH, attached triangulation matching the
inch-scale geometry. Rescale to millimetres. B-rep edges are 25.4 mm; triangulation
vertices are 1.0 mm.

Byte assertions:
  contains(b'TRIANGULATED_FACE')
  contains(b'INCH')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U037",
    defect=(
        "RescaleGeometry does not rescale triangulations — B-rep rescaled but mesh not; "
        "input: STEP file with CONVERSION_BASED_UNIT('INCH') and LENGTH_UNIT = INCH "
        "containing a 1x1x1 inch cube with an attached TRIANGULATED_FACE mesh; "
        "the TRIANGULATED_FACE vertices are at 1.0-inch scale (x,y,z in {0,1}); "
        "after RescaleGeometry converts from INCH to MM, the B-rep coordinates are "
        "rescaled to 25.4 mm per side but the TRIANGULATED_FACE vertices remain at 1.0 mm; "
        "the part has B-rep edges 25.4 mm long and triangulation vertices 1.0 mm apart — "
        "25.4x scale mismatch between the two representations; "
        "kernel rescale must walk every representation form: B-rep, mesh, polyline, point cloud; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: RescaleGeometry skips triangulation, B-rep rescaled but mesh not, "
        "triangulation at wrong scale after rescale, OCCT rescale partial across representations, "
        "mesh scale wrong after unit conversion"
    ),
)


def _render_u037() -> str:
    """Render a Part-21 with INCH unit, B-rep cube, and TRIANGULATED_FACE mesh at inch scale."""
    return (
        "ISO-10303-21;\n"
        "/* U037: RescaleGeometry rescales B-rep but skips TRIANGULATED_FACE mesh */\n"
        "/* File declares INCH; 1x1x1 cube has B-rep coords and mesh coords both at inch scale */\n"
        "/* DEFECT: after RescaleGeometry to MM, B-rep becomes 25.4 mm but mesh stays 1.0 mm */\n"
        "/* Kernel must rescale all representation forms consistently */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U037: INCH cube with TRIANGULATED_FACE — rescale skips mesh'),'2;1');\n"
        "FILE_NAME('U037.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
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
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* B-rep geometry: 1x1x1 inch cube corners (values in inches) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(1.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,1.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,1.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(1.0,1.0,1.0));\n"
        "/* TRIANGULATED_FACE mesh at inch scale */\n"
        "/* Mesh vertices: same 1-inch unit coords — RescaleGeometry skips these */\n"
        "#20=COORDINATES_LIST('cube_mesh_nodes',3,\n"
        "  ((0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),\n"
        "   (0.,0.,1.),(1.,0.,1.),(1.,1.,1.),(0.,1.,1.)));\n"
        "/* DEFECT: TRIANGULATED_FACE vertices at inch scale; B-rep will be rescaled to mm */\n"
        "#21=TRIANGULATED_FACE('cube_bottom_face',#20,.F.,2,\n"
        "  ((1,2,3),(1,3,4)));\n"
        "#22=TRIANGULATED_FACE('cube_top_face',#20,.F.,2,\n"
        "  ((5,6,7),(5,7,8)));\n"
        "/* Geometric curve set: model entity for ARCHETYPE-A — OCC returns empty shape */\n"
        "#30=GEOMETRIC_CURVE_SET('rescale-skips-triangulation',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u037(path) -> None:
    Path(path).write_text(_render_u037())


f.render = _render_u037  # type: ignore[method-assign]
f.write = _write_u037    # type: ignore[method-assign]
