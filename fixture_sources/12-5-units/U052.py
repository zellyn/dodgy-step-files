"""U052 -- REPRESENTATION_CONTEXT of the wrong kind (missing unit mixins) directly governing a live shell.

Sibling of U051, closing the other named subvariant of exchange GAP
`stp-missing-unit-context-default`: "representation context null or of
unusable kind -> default units" (occt-coverage/exchange/problems.json). Here
the context_of_items slot is NOT null -- it references a real, present
REPRESENTATION_CONTEXT('','3D') entity -- but that entity is the plain,
non-complex EXPRESS type, lacking the GeometricRepresentationContext +
GlobalUnitAssignedContext mixins every correctly-formed STEP unit context
carries. Distinct from U051 (context slot literally $/absent).

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  STEPControl_ActorRead::PrepareUnits (STEPControl_ActorRead.cxx:1784-1859):
    Handle(StepRepr_RepresentationContext) theRepCont = rep->ContextOfItems();
    if (theRepCont.IsNull()) { ... return; }   // NOT this fixture's path -- U051's
    ...
    if (theRepCont->IsKind(STANDARD_TYPE(StepGeom_GeometricRepresentationContextAndGlobalUnitAssignedContext))) {
      ... theGUAC = theGRCAGAUC->GlobalUnitAssignedContext();
    }
    ...
    if (!theGUAC.IsNull()) { stat1 = myUnit.ComputeFactors(theGUAC, theLocalFactors); ... }
    // theGUAC stays Null when theRepCont is a bare REPRESENTATION_CONTEXT (wrong
    // kind) -- the ComputeFactors block is silently skipped, no length-factor
    // warning is even emitted, and theLocalFactors keeps its prior/default value.
    if (myUnit.HasUncertainty()) { myPrecision = ...; }
    else {
      TP->AddWarning(theRepCont,"No Length Uncertainty, value of read.precision.val is taken");
      myPrecision = aStepModel->InternalParameters.ReadPrecisionVal;
    }
  theRepCont is present (non-null) so PrepareUnits does NOT hit the "Bad
  RepresentationContext" branch -- it silently falls through the entire
  GeometricRepresentationContextAndGlobalUnitAssignedContext dispatch (the
  context is the WRONG kind to match either complex-type check), leaving
  theGUAC null and the uncertainty/precision defaulted -- the "unusable kind"
  subvariant named explicitly in problems.json's subvariant list.

Live-verified (2026-07-12, OCP 7.8.1 STEPControl_Reader, direct probing --
not mirrored/guessed): shape_null=False, n_faces_total=1. The reader still
returns a live, correctly-topologized shell despite the unusable context.

Byte assertions:
  contains(b"REPRESENTATION_CONTEXT('wrong_kind_ctx','3D')")
  matches -- SHAPE_REPRESENTATION('wrong_kind_shape',(#N),#M) literal form

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U052",
    defect=(
        "SHAPE_REPRESENTATION.context_of_items = a bare REPRESENTATION_CONTEXT('wrong_kind_ctx','3D') "
        "-- present but missing the GeometricRepresentationContext+GlobalUnitAssignedContext mixins -- "
        "directly governing a live ADVANCED_FACE/OPEN_SHELL/SHELL_BASED_SURFACE_MODEL; PrepareUnits's "
        "theGUAC stays Null (wrong-kind context fails both complex-type IsKind checks), unit factors "
        "silently default, reader still returns a live, non-null shape; distinct from U051 (context "
        "slot literally $/absent, not merely wrong-kind); "
        "synonyms: STEP no units defaulted, kernel guessed units, representation context of unusable "
        "kind, bad RepresentationContext missing unit mixins"
    ),
)


def _render_u052() -> str:
    return (
        "ISO-10303-21;\n"
        "/* U052: REPRESENTATION_CONTEXT of the wrong kind (missing unit mixins), directly governing a live shell */\n"
        "/* DEFECT: theRepCont is present but neither GeometricRepresentationContextAndGlobalUnitAssignedContext */\n"
        "/* nor the +GlobalUncertaintyAssignedContext complex kind -- theGUAC stays Null, units silently default */\n"
        "/* Byte assertion: literal form SHAPE_REPRESENTATION('wrong_kind_shape',(#N),#M) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U052: wrong-kind REPRESENTATION_CONTEXT on a live shell'),'2;1');\n"
        "FILE_NAME('U052.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#2=DIRECTION('',(0.0,0.0,1.0));\n"
        "#3=DIRECTION('',(1.0,0.0,0.0));\n"
        "#4=AXIS2_PLACEMENT_3D('',#1,#2,#3);\n"
        "#5=PLANE('',#4);\n"
        "#6=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#7=CARTESIAN_POINT('',(1.0,0.0,0.0));\n"
        "#8=CARTESIAN_POINT('',(1.0,1.0,0.0));\n"
        "#9=CARTESIAN_POINT('',(0.0,1.0,0.0));\n"
        "#10=VERTEX_POINT('',#6);\n"
        "#11=VERTEX_POINT('',#7);\n"
        "#12=VERTEX_POINT('',#8);\n"
        "#13=VERTEX_POINT('',#9);\n"
        "#14=DIRECTION('',(1.0,0.0,0.0));\n"
        "#15=VECTOR('',#14,1.0);\n"
        "#16=LINE('',#6,#15);\n"
        "#17=EDGE_CURVE('',#10,#11,#16,.T.);\n"
        "#18=DIRECTION('',(0.0,1.0,0.0));\n"
        "#19=VECTOR('',#18,1.0);\n"
        "#20=LINE('',#7,#19);\n"
        "#21=EDGE_CURVE('',#11,#12,#20,.T.);\n"
        "#22=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#23=VECTOR('',#22,1.0);\n"
        "#24=LINE('',#8,#23);\n"
        "#25=EDGE_CURVE('',#12,#13,#24,.T.);\n"
        "#26=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#27=VECTOR('',#26,1.0);\n"
        "#28=LINE('',#9,#27);\n"
        "#29=EDGE_CURVE('',#13,#10,#28,.T.);\n"
        "#30=ORIENTED_EDGE('',$,$,#17,.T.);\n"
        "#31=ORIENTED_EDGE('',$,$,#21,.T.);\n"
        "#32=ORIENTED_EDGE('',$,$,#25,.T.);\n"
        "#33=ORIENTED_EDGE('',$,$,#29,.T.);\n"
        "#34=EDGE_LOOP('',(#30,#31,#32,#33));\n"
        "#35=FACE_OUTER_BOUND('',#34,.T.);\n"
        "#36=ADVANCED_FACE('',(#35),#5,.T.);\n"
        "#37=OPEN_SHELL('',(#36));\n"
        "#38=SHELL_BASED_SURFACE_MODEL('',(#37));\n"
        "#100=APPLICATION_CONTEXT('mechanical design');\n"
        "#101=PRODUCT_CONTEXT('',#100,'mechanical');\n"
        "#102=PRODUCT('U052','U052','',(#101));\n"
        "#103=PRODUCT_DEFINITION_FORMATION('','',#102);\n"
        "#104=PRODUCT_DEFINITION_CONTEXT('part definition',#100,'design');\n"
        "#105=PRODUCT_DEFINITION('','',#103,#104);\n"
        "#106=PRODUCT_DEFINITION_SHAPE('','',#105);\n"
        "/* DEFECT: bare REPRESENTATION_CONTEXT -- present but missing GeometricRepresentationContext + */\n"
        "/* GlobalUnitAssignedContext mixins -- 'wrong kind' for PrepareUnits's complex-type dispatch */\n"
        "#99=REPRESENTATION_CONTEXT('wrong_kind_ctx','3D');\n"
        "#107=SHAPE_REPRESENTATION('wrong_kind_shape',(#38),#99);\n"
        "#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u052(path) -> None:
    Path(path).write_text(_render_u052())


f.render = _render_u052  # type: ignore[method-assign]
f.write = _write_u052    # type: ignore[method-assign]
