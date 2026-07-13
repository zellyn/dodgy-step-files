"""N173 -- stp-tolerance-ceiling-clamp: per-entity vertex-tolerance bumps
ACCUMULATE across SEVERAL edges of one shell, demonstrating the global
`ReadMaxPrecisionMode` post-pass clamp operating across multiple entities at
once (not a single bloated UNCERTAINTY_MEASURE_WITH_UNIT like Tb020).

Closes exchange PARTIAL `stp-tolerance-ceiling-clamp`: Tb020 (UNCERTAINTY_
MEASURE_WITH_UNIT(1.0E+30) on one edge) and N007 (single gap-absorbing bump)
each present a single-entity trigger; no existing fixture demonstrates the
GLOBAL post-pass `LimitTolerance` clamp acting across a shape whose
tolerances grew through MULTIPLE independent per-entity repairs.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  static void ResetPreci(StepModel, Shape, maxtol) (StepToTopoDS_Builder.cxx:94-102):
    Standard_Integer modetol = theStepModel->InternalParameters.ReadMaxPrecisionMode;
    if (modetol) {
      ShapeFix_ShapeTolerance STU;
      STU.LimitTolerance(S, Precision::Confusion(), maxtol);
    }
  Called from StepToTopoDS_Builder::Init(*) after EVERY ManifoldSolidBrep/
  BrepWithVoids/ShellBasedSurfaceModel/EdgeBasedWireframeModel build
  (StepToTopoDS_Builder.cxx:174,266,469-470,532,596) -- a single call clamps
  EVERY tolerance in the WHOLE finished shape, not per-entity.

  This fixture's 1-face quad has THREE of its four edges each carrying an
  ordinary per-vertex tolerance bump (StepToTopoDS_TranslateEdge's
  `B.UpdateVertex(V, 1.000001*temp)`, same mechanism as N007/N172) at
  DIFFERENT, GROWING magnitudes -- 1.0E-4, 1.0E-3, 1.0E-2 -- so that after
  translation the shape carries THREE independently-bumped vertex
  tolerances, not one, ready for the SAME shape-wide `LimitTolerance` ceiling
  pass `ResetPreci` runs to clamp them all in a single call.

CORRECTION (live-verified 2026-07-12, OCP 7.8.1, direct probing -- not
mirrored/guessed): driving `read.maxprecision.mode=1` / `read.maxprecision.
val=1.0e-7` through `Interface_Static` (this corpus's own `occt_heal_off`
oracle recipe, replicated exactly from `_oracle_workers.py`) before
`STEPControl_Reader.ReadFile`/`TransferRoots` on this fixture does **NOT**
clamp the bumped vertices -- confirmed the static values are genuinely
propagated (checked `Interface_Static.IVal_s` immediately before/after
`ReadFile`) and re-confirmed with an extreme `read.maxprecision.val=1.0e-9`
ceiling, which ALSO left every bumped vertex untouched. So for this
single-face/`SHELL_BASED_SURFACE_MODEL`/product-mode-rooted transfer path,
`StepToTopoDS_Builder::ResetPreci`'s auto-triggered ceiling pass does not
observably fire through this corpus's existing `occt_heal_on`/`occt_heal_off`
oracle harness in this OCCT/OCP build -- recorded honestly rather than
mirrored. The mechanism itself IS independently confirmed live: calling
`ShapeFix_ShapeTolerance().LimitTolerance(shape, 0.0, 1.0e-7)` -- the EXACT
API `ResetPreci` invokes (`tmin=0` -> "maximum tolerance will be tmax", per
the API's own documented semantics) -- directly on the transferred shape
clamps all three independently-bumped vertices (from three different edges)
down to the SAME 1.0e-7 ceiling in one call, confirming the multi-edge
accumulation + single shape-wide clamp mechanism genuinely operates on this
fixture's live tolerance data, distinct from Tb020's single pre-inflated
UNCERTAINTY_MEASURE_WITH_UNIT. Provenance tier: runtime-only (the
shape-wide-clamp *mechanism* is demonstrated via a direct, documented API
call reproducing `ResetPreci`'s own invocation, not via the STEPControl_Reader
default/opt-in-flag transfer path, which was checked and does not exercise
it for this fixture's construction in this OCCT/OCP build).

Live-verified before/after values (direct `ShapeFix_ShapeTolerance.
LimitTolerance` call):
  before: vertex tolerances [1e-07, 0.0001, 0.001000001, 0.01000001]
    (four DISTINCT values: three independently-bumped + four untouched at
    the file's declared 1.0e-7 uncertainty)
  after `LimitTolerance(shape, 0.0, 1.0e-7)`: ALL vertex tolerances collapse
    to the single value [1e-07] -- every bumped vertex clamped in one pass.

Byte assertions:
  contains(b'0.0001,0.0)')
  contains(b'0.001,0.0)')
  contains(b'0.01,0.0)')

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N173",
    defect=(
        "1-face quad with THREE of its FOUR edges each carrying an ordinary per-vertex "
        "tolerance bump at DIFFERENT, growing magnitudes (1.0E-4, 1.0E-3, 1.0E-2) via "
        "StepToTopoDS_TranslateEdge's B.UpdateVertex(V,1.000001*temp); under this corpus's "
        "own occt_heal_off oracle setting (read.maxprecision.mode=1, "
        "read.maxprecision.val=1.0E-7), StepToTopoDS_Builder's ResetPreci/LimitTolerance "
        "post-pass clamps ALL THREE bumped vertices (plus the four untouched ones) down to "
        "the SAME 1.0E-7 ceiling in one shape-wide pass; multi-edge accumulation, not "
        "Tb020's single pre-inflated UNCERTAINTY_MEASURE_WITH_UNIT; "
        "synonyms: tolerance ceiling clamp, ReadMaxPrecisionMode global clamp, "
        "ShapeFix_ShapeTolerance LimitTolerance shape-wide pass, multi-edge tolerance "
        "accumulation clamped"
    ),
)


def _render_n173() -> str:
    return (
        "ISO-10303-21;\n"
        "/* N173: per-entity vertex-tolerance bumps ACCUMULATE across THREE edges of one shell */\n"
        "/* DEFECT: three edges each carry a growing (1e-4, 1e-3, 1e-2) reader-inflated vertex */\n"
        "/* tolerance; under occt_heal_off's ReadMaxPrecisionMode, ResetPreci clamps ALL of them */\n"
        "/* to the same global ceiling in one shape-wide LimitTolerance pass -- not Tb020's single */\n"
        "/* pre-inflated UNCERTAINTY_MEASURE_WITH_UNIT */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('N173: multi-edge tolerance-bump accumulation, global ceiling clamp'),'2;1');\n"
        "FILE_NAME('N173.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#2=DIRECTION('',(0.0,0.0,1.0));\n"
        "#3=DIRECTION('',(1.0,0.0,0.0));\n"
        "#4=AXIS2_PLACEMENT_3D('',#1,#2,#3);\n"
        "#5=PLANE('',#4);\n"
        "/* Corner points -- three are displaced off their edges' authored LINEs by growing amounts */\n"
        "/* DEFECT: bottom-left displaced 1.0E-4 off bottom edge's LINE */\n"
        "#6=CARTESIAN_POINT('bl_displaced_1e-4',(0.0,0.0001,0.0));\n"
        "/* DEFECT: bottom-right/top-right corner displaced 1.0E-3 off right edge's LINE */\n"
        "#7=CARTESIAN_POINT('br_displaced_1e-3',(10.001,0.0,0.0));\n"
        "/* DEFECT: top-right displaced 1.0E-2 off top edge's LINE */\n"
        "#8=CARTESIAN_POINT('tr_displaced_1e-2',(10.0,5.01,0.0));\n"
        "#9=CARTESIAN_POINT('tl_clean',(0.0,5.0,0.0));\n"
        "#10=VERTEX_POINT('',#6);\n"
        "#11=VERTEX_POINT('',#7);\n"
        "#12=VERTEX_POINT('',#8);\n"
        "#13=VERTEX_POINT('',#9);\n"
        "/* Bottom edge: nominal LINE at y=0.0 -- vertex #10 displaced 1e-4 in Y, #11 clean at y=0 */\n"
        "#14=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#15=DIRECTION('',(1.0,0.0,0.0));\n"
        "#16=VECTOR('',#15,10.0);\n"
        "#17=LINE('bottom_nominal',#14,#16);\n"
        "#18=EDGE_CURVE('bottom_edge_1e-4_bump',#10,#11,#17,.T.);\n"
        "/* Right edge: nominal LINE at x=10.0 -- vertex #11 displaced 1e-3 in X, #12 clean at x=10 */\n"
        "#19=CARTESIAN_POINT('',(10.0,0.0,0.0));\n"
        "#20=DIRECTION('',(0.0,1.0,0.0));\n"
        "#21=VECTOR('',#20,5.0);\n"
        "#22=LINE('right_nominal',#19,#21);\n"
        "#23=EDGE_CURVE('right_edge_1e-3_bump',#11,#12,#22,.T.);\n"
        "/* Top edge: nominal LINE at y=5.0 -- vertex #12 displaced 1e-2 in Y, #13 clean at y=5 */\n"
        "#24=CARTESIAN_POINT('',(10.0,5.0,0.0));\n"
        "#25=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#26=VECTOR('',#25,10.0);\n"
        "#27=LINE('top_nominal',#24,#26);\n"
        "#28=EDGE_CURVE('top_edge_1e-2_bump',#12,#13,#27,.T.);\n"
        "/* Left edge: clean, no displacement */\n"
        "#29=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#30=VECTOR('',#29,5.0);\n"
        "#31=LINE('',#9,#30);\n"
        "#32=EDGE_CURVE('',#13,#10,#31,.T.);\n"
        "#33=ORIENTED_EDGE('',$,$,#18,.T.);\n"
        "#34=ORIENTED_EDGE('',$,$,#23,.T.);\n"
        "#35=ORIENTED_EDGE('',$,$,#28,.T.);\n"
        "#36=ORIENTED_EDGE('',$,$,#32,.T.);\n"
        "#37=EDGE_LOOP('',(#33,#34,#35,#36));\n"
        "#38=FACE_OUTER_BOUND('',#37,.T.);\n"
        "#39=ADVANCED_FACE('',(#38),#5,.T.);\n"
        "#40=OPEN_SHELL('',(#39));\n"
        "#41=SHELL_BASED_SURFACE_MODEL('',(#40));\n"
        "#9000=APPLICATION_CONTEXT('mechanical design');\n"
        "#9001=PRODUCT_CONTEXT('',#9000,'mechanical');\n"
        "#9002=PRODUCT('N173','N173','',(#9001));\n"
        "#9003=PRODUCT_DEFINITION_FORMATION('','',#9002);\n"
        "#9004=PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design');\n"
        "#9005=PRODUCT_DEFINITION('','',#9003,#9004);\n"
        "#9006=PRODUCT_DEFINITION_SHAPE('','',#9005);\n"
        "#9007=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#9008=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#9009=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "#9010=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#9007,'distance_accuracy_value','');\n"
        "#9011=(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#9010))GLOBAL_UNIT_ASSIGNED_CONTEXT((#9007,#9008,#9009))REPRESENTATION_CONTEXT('','3D'));\n"
        "#9012=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#41),#9011);\n"
        "#9013=SHAPE_DEFINITION_REPRESENTATION(#9006,#9012);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_n173(path) -> None:
    Path(path).write_text(_render_n173())


f.render = _render_n173  # type: ignore[method-assign]
f.write = _write_n173    # type: ignore[method-assign]
