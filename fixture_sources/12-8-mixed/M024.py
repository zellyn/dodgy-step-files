"""M024 — Mesh-to-BRep gaps at trim curves (non-watertight result).

Catalog claim: When a mesh is fitted with NURBS patches per region and adjacent
patches' boundary curves are fitted independently, the two curves miss along a
tolerance-exceeding gap. The B-rep is visually closed but non-watertight.

Reproducer recipe: Two adjacent planar quads (left and right halves of a rectangle)
sharing an interior edge. The right quad's left edge sits at x=1.0001 instead of
x=1.0 — a 100-micron gap that exceeds the declared accuracy of 1.0e-6.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M024",
    schema="AP214",
    defect=(
        "Mesh-to-BRep gaps at trim curves (non-watertight result); "
        "input: STEP file with two adjacent planar ADVANCED_FACEs sharing an interior "
        "edge where independent patch fitting left a 100-micron gap: "
        "left face right edge at x=1.0, right face left edge at x=1.0001; "
        "gap of 0.0001 mm exceeds declared tolerance of 1.0e-6 mm; "
        "B-rep appears visually closed but downstream watertightness check fails; "
        "kernel must heal: enforce watertightness as a fitting constraint; "
        "OCC validity-checker does not flag sub-tolerance trim gaps; "
        "synonyms: mesh-to-BRep gaps at trims, non-watertight reverse-engineered face, "
        "patch fitting leaves trim gaps, STL-to-NURBS not watertight"
    ),
)


def _render_m024() -> str:
    lines = []
    lines.append("ISO-10303-21;")
    lines.append(f"/* M024: {f.defect} */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M024'),'2;1');")
    lines.append("FILE_NAME('M024.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('automotive_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-6),#10,'distance_accuracy_value','');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("     GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("     GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("     REPRESENTATION_CONTEXT('part','3D'));")
    lines.append("/* Left quad: x in [0,1], y in [0,1] */")
    lines.append("#100=CARTESIAN_POINT('L_v0',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('L_v1',(1.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('L_v2',(1.0,1.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('L_v3',(0.0,1.0,0.0));")
    lines.append("/* Right quad: x in [1.0001,2.0001] — 100-micron gap on left edge */")
    lines.append("#110=CARTESIAN_POINT('R_v0',(1.0001,0.0,0.0));")
    lines.append("#111=CARTESIAN_POINT('R_v1',(2.0001,0.0,0.0));")
    lines.append("#112=CARTESIAN_POINT('R_v2',(2.0001,1.0,0.0));")
    lines.append("#113=CARTESIAN_POINT('R_v3',(1.0001,1.0,0.0));")
    lines.append("#120=VERTEX_POINT('',#100);")
    lines.append("#121=VERTEX_POINT('',#101);")
    lines.append("#122=VERTEX_POINT('',#102);")
    lines.append("#123=VERTEX_POINT('',#103);")
    lines.append("#124=VERTEX_POINT('',#110);")
    lines.append("#125=VERTEX_POINT('',#111);")
    lines.append("#126=VERTEX_POINT('',#112);")
    lines.append("#127=VERTEX_POINT('',#113);")
    lines.append("/* Directions and vectors */")
    lines.append("#200=DIRECTION('',(0.0,0.0,1.0));")
    lines.append("#201=DIRECTION('',(1.0,0.0,0.0));")
    lines.append("#210=DIRECTION('',(1.0,0.0,0.0));")
    lines.append("#211=VECTOR('',#210,1.0);")
    lines.append("#212=DIRECTION('',(0.0,1.0,0.0));")
    lines.append("#213=VECTOR('',#212,1.0);")
    lines.append("/* Left face plane and edges */")
    lines.append("#202=AXIS2_PLACEMENT_3D('',#100,#200,#201);")
    lines.append("#203=PLANE('left_plane',#202);")
    lines.append("#220=LINE('',#100,#211);")
    lines.append("#221=EDGE_CURVE('',#120,#121,#220,.T.);")
    lines.append("#222=LINE('',#101,#213);")
    lines.append("#223=EDGE_CURVE('',#121,#122,#222,.T.);")
    lines.append("#224=LINE('',#103,#211);")
    lines.append("#225=EDGE_CURVE('',#123,#122,#224,.T.);")
    lines.append("#226=LINE('',#100,#213);")
    lines.append("#227=EDGE_CURVE('',#120,#123,#226,.T.);")
    lines.append("#230=ORIENTED_EDGE('',*,*,#221,.T.);")
    lines.append("#231=ORIENTED_EDGE('',*,*,#223,.T.);")
    lines.append("#232=ORIENTED_EDGE('',*,*,#225,.F.);")
    lines.append("#233=ORIENTED_EDGE('',*,*,#227,.F.);")
    lines.append("#234=EDGE_LOOP('',(#230,#231,#232,#233));")
    lines.append("#235=FACE_OUTER_BOUND('',#234,.T.);")
    lines.append("#236=ADVANCED_FACE('left_face',(#235),#203,.T.);")
    lines.append("/* Right face plane and edges (offset by 100 microns from left face) */")
    lines.append("#300=AXIS2_PLACEMENT_3D('',#110,#200,#201);")
    lines.append("#301=PLANE('right_plane',#300);")
    lines.append("#302=DIRECTION('',(1.0,0.0,0.0));")
    lines.append("#303=VECTOR('',#302,1.0);")
    lines.append("#304=DIRECTION('',(0.0,1.0,0.0));")
    lines.append("#305=VECTOR('',#304,1.0);")
    lines.append("#310=LINE('',#110,#303);")
    lines.append("#311=EDGE_CURVE('',#124,#125,#310,.T.);")
    lines.append("#312=LINE('',#111,#305);")
    lines.append("#313=EDGE_CURVE('',#125,#126,#312,.T.);")
    lines.append("#314=LINE('',#113,#303);")
    lines.append("#315=EDGE_CURVE('',#127,#126,#314,.T.);")
    lines.append("#316=LINE('',#110,#305);")
    lines.append("#317=EDGE_CURVE('',#124,#127,#316,.T.);")
    lines.append("#318=ORIENTED_EDGE('',*,*,#311,.T.);")
    lines.append("#319=ORIENTED_EDGE('',*,*,#313,.T.);")
    lines.append("#320=ORIENTED_EDGE('',*,*,#315,.F.);")
    lines.append("#321=ORIENTED_EDGE('',*,*,#317,.F.);")
    lines.append("#322=EDGE_LOOP('',(#318,#319,#320,#321));")
    lines.append("#323=FACE_OUTER_BOUND('',#322,.T.);")
    lines.append("#324=ADVANCED_FACE('right_face',(#323),#301,.T.);")
    lines.append("/* OPEN_SHELL: the gap means it cannot be sewn into a CLOSED_SHELL.")
    lines.append("   Non-watertight: shared edge has 100-micron gap between left and right faces. */")
    lines.append("#400=OPEN_SHELL('non_watertight',(#236,#324));")
    lines.append("#410=SHELL_BASED_SURFACE_MODEL('',(#400));")
    lines.append("#420=ADVANCED_BREP_SHAPE_REPRESENTATION('',(#410),#14);")
    lines.append("/* PRODUCT chain */")
    lines.append("#9010=PRODUCT_CONTEXT('',#1,'mechanical');")
    lines.append("#9011=PRODUCT('M024','M024','',(#9010));")
    lines.append("#9012=PRODUCT_DEFINITION_FORMATION('','',#9011);")
    lines.append("#9013=PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');")
    lines.append("#9014=PRODUCT_DEFINITION('','',#9012,#9013);")
    lines.append("#9015=PRODUCT_DEFINITION_SHAPE('','',#9014);")
    lines.append("#9051=SHAPE_DEFINITION_REPRESENTATION(#9015,#420);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m024(path) -> None:
    _Path(path).write_text(_render_m024())


f.render = _render_m024   # type: ignore[method-assign]
f.write  = _write_m024    # type: ignore[method-assign]
