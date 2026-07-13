"""N172 -- seq-set-tolerance, "tolerance outside acceptable band" clamp
subvariant, on a live face (not N001's dead GEOMETRIC_CURVE_SET scaffold).

Closes exchange PARTIAL `seq-set-tolerance`'s missing subvariant (a): the
VERDICT_AUDIT.md 2026-07-01 overturn downgraded this class COVERED->PARTIAL
specifically because subvariant (a) "tolerance outside band" rested solely on
N001, a faceless GEOMETRIC_CURVE_SET wireframe with shape_null==True (no
translated shape ever carries the declared tolerance hierarchy). This fixture
reaches the SAME `settol` operator (`ShapeProcess_OperLibrary.cxx:163-186`,
registered as the "SetTolerance" ShapeProcess operator) on a REAL translated
face whose vertex tolerance is bumped by ordinary reader tolerance-inflation
(same StepToTopoDS_TranslateEdge mechanism as N007/N174) to a value that
lands OUTSIDE a realistic `[val/ratio, val*ratio]` target band.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  static Standard_Boolean settol(ctx, ...) (ShapeProcess_OperLibrary.cxx:163-186):
    if (ctx->IntegerVal("Mode",0)>0 && ctx->GetReal("Value",val)) {
      Standard_Real rat = ctx->RealVal("Ratio",1.);
      if (rat >= 1) {
        ShapeFix_ShapeTolerance SFST;
        SFST.LimitTolerance(ctx->Result(), val/rat, val*rat);
      }
    }
  `settol` is an opt-in `ShapeProcess` sequence operator (same category as
  `dropsmallsolids`, already used by this corpus's Tsh238/Tsh239), not run by
  STEPControl_Reader's default transfer. This fixture's job is to deliver a
  live shape whose ACTUAL vertex tolerance genuinely falls outside a
  realistic target band, so that running `settol` against it is observable
  (not a no-op).

  Construction: a 1-face quad whose bottom-left vertex is displaced 0.05 mm
  (far larger than N007/N174's 0.001 mm) from its edge's authored LINE along
  a direction that is NOT shared by the opposite endpoint (temp1=0.05,
  temp2=0.0 -- the ordinary per-vertex-bump path, not the line-shift path),
  so `StepToTopoDS_TranslateEdge::MakeFromCurve3D`'s `B.UpdateVertex(V,
  1.000001*temp1)` bumps that one vertex's tolerance to ~0.050 00005 mm --
  three orders of magnitude above the file's declared model uncertainty
  (1.0E-7 mm) and any realistic `[val/ratio, val*ratio]` band derived from
  it.

Live-verified (2026-07-12, OCP 7.8.1, direct probing -- not mirrored/
guessed): after `STEPControl_Reader.TransferRoots()`, the displaced vertex's
tolerance is 0.0500000500... (== 1.000001*0.05). Applying
`ShapeFix_ShapeTolerance().LimitTolerance(shape, 1.0E-4, 1.0E-2)` (the exact
API `settol` invokes, target band [val/ratio,val*ratio] with val=1.0E-3,
ratio=10) on this live shape returns True (at least one tolerance modified)
and clamps that vertex's tolerance down to 1.0E-2 -- confirming the "outside
band -> clamp" mechanism is genuinely reachable on live, reader-produced
tolerance data, not just on N001's dead scaffold.

Byte assertions:
  contains(b'0.05,0.0)')
  count_entity_def(b'VERTEX_POINT') == 4

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N172",
    defect=(
        "one vertex of a live quad face is displaced 0.05mm from its edge's authored LINE "
        "(only that endpoint -- the ordinary per-vertex bump path, not N174's line-shift "
        "path); StepToTopoDS_TranslateEdge bumps that vertex's tolerance to "
        "1.000001*0.05~=0.0500000500, three orders of magnitude above the file's declared "
        "1.0E-7 model uncertainty; the ShapeProcess 'SetTolerance' operator (settol, "
        "ShapeProcess_OperLibrary.cxx:163-186) calls ShapeFix_ShapeTolerance::LimitTolerance "
        "into a [val/ratio,val*ratio] band -- this vertex's tolerance genuinely falls outside "
        "any realistic band derived from the declared uncertainty, unlike N001's dead "
        "GEOMETRIC_CURVE_SET scaffold (shape_null==True, no live tolerance to clamp); "
        "synonyms: tolerance outside acceptable band, settol clamp, ShapeFix_ShapeTolerance "
        "LimitTolerance band violation, reader-inflated vertex tolerance exceeds target ratio"
    ),
)


def _render_n172() -> str:
    return (
        "ISO-10303-21;\n"
        "/* N172: seq-set-tolerance 'outside acceptable band' clamp subvariant, on a live face */\n"
        "/* DEFECT: bottom-left vertex displaced 0.05mm from its edge's authored LINE -- reader */\n"
        "/* tolerance-inflation bumps that vertex to ~0.05mm, far outside any realistic settol band */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('N172: seq-set-tolerance outside-band clamp subvariant, live face'),'2;1');\n"
        "FILE_NAME('N172.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#2=DIRECTION('',(0.0,0.0,1.0));\n"
        "#3=DIRECTION('',(1.0,0.0,0.0));\n"
        "#4=AXIS2_PLACEMENT_3D('',#1,#2,#3);\n"
        "#5=PLANE('',#4);\n"
        "/* DEFECT: bottom-left vertex displaced 0.05mm off the authored LINE's y=0.0; the other */\n"
        "/* endpoint (bottom-right, #7) is NOT displaced -- ordinary per-vertex bump, not line-shift */\n"
        "#6=CARTESIAN_POINT('bottom_left_displaced_0p05',(0.0,0.05,0.0));\n"
        "#7=CARTESIAN_POINT('',(10.0,0.0,0.0));\n"
        "#8=CARTESIAN_POINT('',(10.0,5.0,0.0));\n"
        "#9=CARTESIAN_POINT('',(0.0,5.0,0.0));\n"
        "#10=VERTEX_POINT('',#6);\n"
        "#11=VERTEX_POINT('',#7);\n"
        "#12=VERTEX_POINT('',#8);\n"
        "#13=VERTEX_POINT('',#9);\n"
        "#14=CARTESIAN_POINT('line_nominal_origin',(0.0,0.0,0.0));\n"
        "#15=DIRECTION('',(1.0,0.0,0.0));\n"
        "#16=VECTOR('',#15,10.0);\n"
        "#17=LINE('bottom_edge_nominal',#14,#16);\n"
        "#18=EDGE_CURVE('bottom_edge_one_vertex_displaced',#10,#11,#17,.T.);\n"
        "#19=DIRECTION('',(0.0,1.0,0.0));\n"
        "#20=VECTOR('',#19,5.0);\n"
        "#21=LINE('',#7,#20);\n"
        "#22=EDGE_CURVE('',#11,#12,#21,.T.);\n"
        "#23=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#24=VECTOR('',#23,10.0);\n"
        "#25=LINE('',#8,#24);\n"
        "#26=EDGE_CURVE('',#12,#13,#25,.T.);\n"
        "#27=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#28=VECTOR('',#27,5.0);\n"
        "#29=LINE('',#9,#28);\n"
        "#30=EDGE_CURVE('',#13,#10,#29,.T.);\n"
        "#31=ORIENTED_EDGE('',$,$,#18,.T.);\n"
        "#32=ORIENTED_EDGE('',$,$,#22,.T.);\n"
        "#33=ORIENTED_EDGE('',$,$,#26,.T.);\n"
        "#34=ORIENTED_EDGE('',$,$,#30,.T.);\n"
        "#35=EDGE_LOOP('',(#31,#32,#33,#34));\n"
        "#36=FACE_OUTER_BOUND('',#35,.T.);\n"
        "#37=ADVANCED_FACE('',(#36),#5,.T.);\n"
        "#38=OPEN_SHELL('',(#37));\n"
        "#39=SHELL_BASED_SURFACE_MODEL('',(#38));\n"
        "#9000=APPLICATION_CONTEXT('mechanical design');\n"
        "#9001=PRODUCT_CONTEXT('',#9000,'mechanical');\n"
        "#9002=PRODUCT('N172','N172','',(#9001));\n"
        "#9003=PRODUCT_DEFINITION_FORMATION('','',#9002);\n"
        "#9004=PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design');\n"
        "#9005=PRODUCT_DEFINITION('','',#9003,#9004);\n"
        "#9006=PRODUCT_DEFINITION_SHAPE('','',#9005);\n"
        "#9007=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#9008=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#9009=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "#9010=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#9007,'distance_accuracy_value','');\n"
        "#9011=(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#9010))GLOBAL_UNIT_ASSIGNED_CONTEXT((#9007,#9008,#9009))REPRESENTATION_CONTEXT('','3D'));\n"
        "#9012=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#39),#9011);\n"
        "#9013=SHAPE_DEFINITION_REPRESENTATION(#9006,#9012);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_n172(path) -> None:
    Path(path).write_text(_render_n172())


f.render = _render_n172  # type: ignore[method-assign]
f.write = _write_n172    # type: ignore[method-assign]
