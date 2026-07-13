"""N174 -- stp-vertex-tol-gap, displaced-line-with-correct-direction subvariant
(PCB/FPX-export quirk): both endpoints show the SAME projection error, so the
repair rigidly shifts the LINE along its own direction instead of merely
enlarging vertex tolerance.

Closes exchange PARTIAL `stp-vertex-tol-gap`'s missing subvariant. N007 (the
existing fixture) covers the ORDINARY-gap case: only ONE endpoint is
displaced (temp1=0.001, temp2=0.0), so `StepToTopoDS_TranslateEdge` takes the
per-vertex tolerance-bump branch. This fixture is the narrower, distinct
line-shift branch: BOTH endpoints of the same edge are displaced by the exact
SAME perpendicular offset from the authored LINE, in a way that preserves the
edge's total length -- the "correct direction, wrong position" signature of
certain PCB/FPX-style exporters.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  StepToTopoDS_TranslateEdge::MakeFromCurve3D, StepToTopoDS_TranslateEdge.cxx:392-431:
    temp1 = pU1.Distance(pv1); temp2 = pU2.Distance(pv2);   // projection gaps
    if (temp1 > preci || temp2 > preci) {
      // bug 25415: FPX Expert 2013 (PCB design) pattern: line displaced from
      // its true position but with correct direction
      if (Abs(temp1 - temp2) < preci &&
          Abs(U2 - U1 - pnt1.Distance(pnt2)) < Precision::Confusion() &&
          C1->IsKind(STANDARD_TYPE(Geom_Line)))
      {
        // rigidly SHIFT the line along its own direction so it passes
        // exactly through the vertices, instead of enlarging tolerance
        gp_Pnt anOrigin = pnt1.XYZ() - aLin.Position().Direction().XYZ() * U1;
        aLin.SetLocation(anOrigin);
        C1 = new Geom_Line(aLin);
        TP->AddWarning(C3D, "Poor result from projection vertex / line 3d, line shifted");
      }
      ...
    }
    B.UpdateVertex(V1, 1.000001*temp1);   // tolerance STILL bumped using the
    B.UpdateVertex(V2, 1.000001*temp2);   // PRE-shift gap, even on this branch

  This fixture's bottom edge of a quad face: LINE authored at y=0 with
  direction (1,0,0) from (0,0,0) to (10,0,0), but its two VERTEX_POINTs sit
  at y=0.001 instead of y=0 -- (0,0.001,0) and (10,0.001,0). Both endpoints
  project onto the nominal line with IDENTICAL gap (temp1==temp2==0.001,
  satisfying `Abs(temp1-temp2)<preci`), and the projected-parameter span
  (U2-U1=10) exactly equals the true vertex-to-vertex distance (also 10,
  since the y-offset is identical at both ends and cancels), satisfying
  `Abs(U2-U1-pnt1.Distance(pnt2))<Precision::Confusion()` -- both gates for
  the line-shift branch. N007's construction instead displaces only ONE
  vertex (temp2==0), which fails `Abs(temp1-temp2)<preci` and takes the
  generic per-vertex bump branch instead.

Live-verified (2026-07-12, OCP 7.8.1, direct probing of the transferred
edge's bound 3D curve -- not mirrored/guessed): the edge's `BRep_Tool::Curve`
after transfer is a `Geom_Line` whose location has been shifted to
(0,0.001,0) -- i.e. genuinely rigidly shifted off the authored (0,0,0) origin
to pass through the displaced vertices, confirming the line-shift branch (not
the generic bump branch) fired. Vertex tolerance on the shifted edge's
endpoints is 1.000001*0.001 ~= 1.000001e-3 (the SAME bump formula as N007,
applied even though the underlying curve was rigidly repositioned).

Byte assertions:
  contains(b'0.001,0.0)')
  count_entity_def(b'VERTEX_POINT') == 4

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N174",
    defect=(
        "LINE authored at y=0 (dir (1,0,0), origin (0,0,0)->(10,0,0)) but BOTH its "
        "VERTEX_POINT endpoints sit at y=0.001 -- (0,0.001,0) and (10,0.001,0) -- an "
        "identical perpendicular offset at both ends preserving the vertex-to-vertex "
        "distance; StepToTopoDS_TranslateEdge's line-shift gate (Abs(temp1-temp2)<preci "
        "AND Abs(U2-U1-dist(pnt1,pnt2))<Precision::Confusion() AND Geom_Line) fires -- "
        "the LINE is rigidly shifted to pass through the vertices instead of merely "
        "enlarging vertex tolerance (FPX/PCB-export quirk, bug 25415); the vertex "
        "tolerance is STILL bumped 1.000001x using the pre-shift gap; N007 displaces "
        "only ONE endpoint (temp1!=temp2), taking the ordinary per-vertex bump path "
        "instead -- this fixture is the narrower, distinct correct-direction subvariant; "
        "synonyms: displaced line correct direction, PCB export line shift, FPX Expert "
        "line shifted vertex gap, rigid line reposition on projection mismatch"
    ),
)


def _render_n174() -> str:
    return (
        "ISO-10303-21;\n"
        "/* N174: LINE displaced from true position but with CORRECT direction (PCB/FPX quirk) */\n"
        "/* DEFECT: both edge endpoints show the SAME 0.001 perpendicular offset from the authored */\n"
        "/* LINE -- StepToTopoDS_TranslateEdge's line-shift branch fires, rigidly repositioning the */\n"
        "/* curve instead of merely enlarging vertex tolerance (bug 25415, FPX Expert PCB pattern) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('N174: displaced-line correct-direction vertex-tol-gap subvariant'),'2;1');\n"
        "FILE_NAME('N174.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#2=DIRECTION('',(0.0,0.0,1.0));\n"
        "#3=DIRECTION('',(1.0,0.0,0.0));\n"
        "#4=AXIS2_PLACEMENT_3D('',#1,#2,#3);\n"
        "#5=PLANE('',#4);\n"
        "/* Bottom-edge vertices displaced +0.001 in Y from the LINE's authored y=0 -- SAME offset both ends */\n"
        "#6=CARTESIAN_POINT('bottom_left_displaced',(0.0,0.001,0.0));\n"
        "#7=CARTESIAN_POINT('bottom_right_displaced',(10.0,0.001,0.0));\n"
        "#8=CARTESIAN_POINT('',(10.0,5.0,0.0));\n"
        "#9=CARTESIAN_POINT('',(0.0,5.0,0.0));\n"
        "#10=VERTEX_POINT('',#6);\n"
        "#11=VERTEX_POINT('',#7);\n"
        "#12=VERTEX_POINT('',#8);\n"
        "#13=VERTEX_POINT('',#9);\n"
        "/* DEFECT: LINE's own CARTESIAN_POINT origin is at y=0.0 -- NOT the vertices' y=0.001 */\n"
        "#14=CARTESIAN_POINT('line_nominal_origin',(0.0,0.0,0.0));\n"
        "#15=DIRECTION('',(1.0,0.0,0.0));\n"
        "#16=VECTOR('',#15,10.0);\n"
        "#17=LINE('bottom_edge_nominal',#14,#16);\n"
        "#18=EDGE_CURVE('bottom_displaced_edge',#10,#11,#17,.T.);\n"
        "#19=DIRECTION('',(0.0,1.0,0.0));\n"
        "#20=VECTOR('',#19,5.0);\n"
        "#21=CARTESIAN_POINT('',(10.0,0.001,0.0));\n"
        "#22=LINE('',#21,#20);\n"
        "#23=EDGE_CURVE('',#11,#12,#22,.T.);\n"
        "#24=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#25=VECTOR('',#24,10.0);\n"
        "#26=LINE('',#8,#25);\n"
        "#27=EDGE_CURVE('',#12,#13,#26,.T.);\n"
        "#28=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#29=VECTOR('',#28,5.0);\n"
        "#30=LINE('',#9,#29);\n"
        "#31=EDGE_CURVE('',#13,#10,#30,.T.);\n"
        "#32=ORIENTED_EDGE('',$,$,#18,.T.);\n"
        "#33=ORIENTED_EDGE('',$,$,#23,.T.);\n"
        "#34=ORIENTED_EDGE('',$,$,#27,.T.);\n"
        "#35=ORIENTED_EDGE('',$,$,#31,.T.);\n"
        "#36=EDGE_LOOP('',(#32,#33,#34,#35));\n"
        "#37=FACE_OUTER_BOUND('',#36,.T.);\n"
        "#38=ADVANCED_FACE('',(#37),#5,.T.);\n"
        "#39=OPEN_SHELL('',(#38));\n"
        "#40=SHELL_BASED_SURFACE_MODEL('',(#39));\n"
        "#9000=APPLICATION_CONTEXT('mechanical design');\n"
        "#9001=PRODUCT_CONTEXT('',#9000,'mechanical');\n"
        "#9002=PRODUCT('N174','N174','',(#9001));\n"
        "#9003=PRODUCT_DEFINITION_FORMATION('','',#9002);\n"
        "#9004=PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design');\n"
        "#9005=PRODUCT_DEFINITION('','',#9003,#9004);\n"
        "#9006=PRODUCT_DEFINITION_SHAPE('','',#9005);\n"
        "#9007=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#9008=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#9009=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "#9010=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#9007,'distance_accuracy_value','');\n"
        "#9011=(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#9010))GLOBAL_UNIT_ASSIGNED_CONTEXT((#9007,#9008,#9009))REPRESENTATION_CONTEXT('','3D'));\n"
        "#9012=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#40),#9011);\n"
        "#9013=SHAPE_DEFINITION_REPRESENTATION(#9006,#9012);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_n174(path) -> None:
    Path(path).write_text(_render_n174())


f.render = _render_n174  # type: ignore[method-assign]
f.write = _write_n174    # type: ignore[method-assign]
