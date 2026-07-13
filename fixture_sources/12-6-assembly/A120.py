"""A120 -- SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION where only ONE
of Origin/Target resolves to its expected representation's item list (the
"does not belong" unrepairable branch) -- A007 is the FULLY-swapped case.

Closes exchange PARTIAL `stp-srrwt-axis-swap`'s missing subvariant. A007
demonstrates the fully-repairable case: BOTH Origin and Target are found
cross-referenced (Origin sits in Target's representation, Target sits in
Origin's), so `ComputeTransformation` transparently swaps them and computes
a (repaired) transform. This fixture is the narrower, distinct
half-resolved case: Origin correctly belongs to its OWN representation's
item list, but Target belongs to NEITHER representation's item list (a
completely foreign placement) -- so the membership check cannot even
determine a consistent swap, and OCCT falls through to the unrepairable
"does not belong" branch, silently computing a transform from the
inconsistent org/trg pair anyway.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  STEPControl_ActorRead::ComputeTransformation, STEPControl_ActorRead.cxx:1886-1946:
    for (i=1..OrigContext->NbItems())
      if (OrigContext->ItemsValue(i)==org) isOKOrigin=True;
      else if (OrigContext->ItemsValue(i)==trg) isSwapTarget=True;
    for (i=1..TargContext->NbItems())
      if (TargContext->ItemsValue(i)==trg) isOKTarget=True;
      else if (TargContext->ItemsValue(i)==org) isSwapOrigin=True;
    if (!isOKOrigin || !isOKTarget) {
      if (isSwapOrigin && isSwapTarget) {
        std::swap(org,trg);
        TP->AddWarning(org, "Axis placements are swapped in SRRWT; corrected");
      } else {
        TP->AddWarning((isOKOrigin ? trg : org),
                        "Axis placement used by SRRWT does not belong to corresponding representation");
      }
    }
    // Trsf computed from (possibly still-wrong) org/trg either way.

  This fixture: Origin (Ax1) IS listed in the Parent representation's items
  (isOKOrigin=True). Target (Ax2) is a placement entity that is NOT listed
  in either the Parent's or the Child's representation items (isOKTarget=
  False, and isSwapTarget/isSwapOrigin both False since Ax2/Ax1 never
  cross-appear) -- the "only one side resolves cleanly" case named in
  problems.json's subvariant list. `ComputeSRRWT`/`ComputeTransformation`
  falls to the else branch, warns "does not belong to corresponding
  representation" for Target, and still computes a Trsf from org/trg as
  given (not rejected).

Structure note: Origin/Target (Ax1/Ax2) are wired through DEDICATED
placement-only representations (`parent_placement_rep`/`child_placement_rep`,
mirroring A007's own `asm_rep`/`cmp_rep` split) rather than the parts' real
geometry-bearing representations -- keeping the SRRWT membership-check inputs
clean (mixing a bare AXIS2_PLACEMENT_3D item into a geometry-bearing
SHAPE_REPRESENTATION's item list was independently tested and found to break
Parent-PD root recognition's own normal shape transfer; A007's established
split avoids that). The parts' REAL geometry (Parent's 1x1 face, Child's 5x5
face) each transfer via their OWN normal, independent PRODUCT_DEFINITION ->
SHAPE_DEFINITION_REPRESENTATION chain (`#47`, `#89`), exactly like A007.

Live-verified (2026-07-12, OCP 7.8.1, direct probing -- not mirrored/
guessed): shape_null=False; `n_faces_total=1` (Parent's own 1x1 face,
transferred via its own SDR chain, bbox `[0,1]x[0,1]` at the origin --
confirmed un-transformed). Since `parent_placement_rep`/`child_placement_rep`
carry no geometry (`Recognize()` does not accept a bare `AXIS2_PLACEMENT_3D`
item), `TransferEntity(CDSR)`'s own contribution resolves to a null/empty
shape and is silently absent from the final compound -- the SRRWT/NAUO/CDSR
defect bytes are present, well-formed, and structurally correct (same
epistemic status as A007's own established, already-shipped SRRWT fixture,
which has the identical placement-only-representation limitation), but the
specific membership-check outcome is confirmed via source-level mechanism
analysis (`STEPConstruct_Assembly::CheckSRRReversesNAUO`/
`STEPControl_ActorRead::ComputeTransformation`, cited above) rather than via
an observable shape-count difference.

Byte assertions:
  contains(b'SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION')
  contains(b'ITEM_DEFINED_TRANSFORMATION')

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="A120",
    defect=(
        "SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION whose ITEM_DEFINED_TRANSFORMATION "
        "has TransformItem1 (Origin, Ax1) genuinely listed in the Parent representation's items "
        "(isOKOrigin=True), but TransformItem2 (Target, Ax2) listed in NEITHER representation's "
        "items -- a completely foreign placement -- so isOKTarget=False and neither "
        "isSwapOrigin nor isSwapTarget is True; ComputeTransformation's cross-swap repair cannot "
        "apply (only A007's FULLY-swapped case can be transparently repaired), so OCCT falls to "
        "the unrepairable 'Axis placement used by SRRWT does not belong to corresponding "
        "representation' branch and silently computes a transform from the inconsistent pair "
        "anyway rather than rejecting the file; "
        "synonyms: SRRWT axis placement does not belong, half-swapped SRRWT, unrepairable "
        "axis-placement mismatch, ComputeTransformation membership check fails one side"
    ),
)


def _render_a120() -> str:
    return (
        "ISO-10303-21;\n"
        "/* A120: SRRWT where only ONE of Origin/Target belongs to its expected representation */\n"
        "/* DEFECT: Origin(Ax1) IS in Parent's items; Target(Ax2) is in NEITHER rep's items -- */\n"
        "/* the unrepairable 'does not belong' branch (A007 is the FULLY-swapped, repairable case) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('A120: SRRWT half-swap, only Origin resolves to its own representation'),'2;1');\n"
        "FILE_NAME('A120.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#100=APPLICATION_CONTEXT('mechanical design');\n"
        "#101=(GEOMETRIC_REPRESENTATION_CONTEXT(3)REPRESENTATION_CONTEXT('','3D'));\n"
        "/* ---- Parent product: 1x1 marker face at the origin ---- */\n"
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
        "#40=SHAPE_REPRESENTATION('parent_rep',(#38),#101);\n"
        "#41=PRODUCT_CONTEXT('',#100,'mechanical');\n"
        "#42=PRODUCT('Parent','Parent','',(#41));\n"
        "#43=PRODUCT_DEFINITION_FORMATION('','',#42);\n"
        "#44=PRODUCT_DEFINITION_CONTEXT('part definition',#100,'design');\n"
        "#45=PRODUCT_DEFINITION('','',#43,#44);\n"
        "#46=PRODUCT_DEFINITION_SHAPE('','',#45);\n"
        "#47=SHAPE_DEFINITION_REPRESENTATION(#46,#40);\n"
        "/* DEFECT setup: a SEPARATE placement-only representation for the assembly relationship -- */\n"
        "/* Ax1 (Origin) IS included in ITS items, so isOKOrigin=True for the SRRWT membership check */\n"
        "#39=CARTESIAN_POINT('ax1_origin',(0.0,0.0,0.0));\n"
        "#60=AXIS2_PLACEMENT_3D('Ax1_Origin',#39,#2,#3);\n"
        "#48=SHAPE_REPRESENTATION('parent_placement_rep',(#60),#101);\n"
        "/* ---- Child product: 5x5 marker face at (100,0,0) ---- */\n"
        "#50=CARTESIAN_POINT('',(100.0,0.0,0.0));\n"
        "#51=AXIS2_PLACEMENT_3D('',#50,#2,#3);\n"
        "#52=PLANE('',#51);\n"
        "#53=CARTESIAN_POINT('',(100.0,0.0,0.0));\n"
        "#54=CARTESIAN_POINT('',(105.0,0.0,0.0));\n"
        "#55=CARTESIAN_POINT('',(105.0,5.0,0.0));\n"
        "#56=CARTESIAN_POINT('',(100.0,5.0,0.0));\n"
        "#57=VERTEX_POINT('',#53);\n"
        "#58=VERTEX_POINT('',#54);\n"
        "#59=VERTEX_POINT('',#55);\n"
        "#61=VERTEX_POINT('',#56);\n"
        "#62=VECTOR('',#14,5.0);\n"
        "#63=LINE('',#53,#62);\n"
        "#64=EDGE_CURVE('',#57,#58,#63,.T.);\n"
        "#65=VECTOR('',#18,5.0);\n"
        "#66=LINE('',#54,#65);\n"
        "#67=EDGE_CURVE('',#58,#59,#66,.T.);\n"
        "#68=VECTOR('',#22,5.0);\n"
        "#69=LINE('',#55,#68);\n"
        "#70=EDGE_CURVE('',#59,#61,#69,.T.);\n"
        "#71=VECTOR('',#26,5.0);\n"
        "#72=LINE('',#56,#71);\n"
        "#73=EDGE_CURVE('',#61,#57,#72,.T.);\n"
        "#74=ORIENTED_EDGE('',$,$,#64,.T.);\n"
        "#75=ORIENTED_EDGE('',$,$,#67,.T.);\n"
        "#76=ORIENTED_EDGE('',$,$,#70,.T.);\n"
        "#77=ORIENTED_EDGE('',$,$,#73,.T.);\n"
        "#78=EDGE_LOOP('',(#74,#75,#76,#77));\n"
        "#79=FACE_OUTER_BOUND('',#78,.T.);\n"
        "#80=ADVANCED_FACE('',(#79),#52,.T.);\n"
        "#81=OPEN_SHELL('',(#80));\n"
        "#82=SHELL_BASED_SURFACE_MODEL('',(#81));\n"
        "#83=SHAPE_REPRESENTATION('child_rep',(#82),#101);\n"
        "#84=PRODUCT_CONTEXT('',#100,'mechanical');\n"
        "#85=PRODUCT('Child','Child','',(#84));\n"
        "#86=PRODUCT_DEFINITION_FORMATION('','',#85);\n"
        "#87=PRODUCT_DEFINITION('','',#86,#44);\n"
        "#88=PRODUCT_DEFINITION_SHAPE('','',#87);\n"
        "#89=SHAPE_DEFINITION_REPRESENTATION(#88,#83);\n"
        "/* Child's SEPARATE placement-only representation for the assembly relationship -- */\n"
        "/* DEFECT: Ax2 (Target) is NOT included in ITS items (nor Parent's placement rep's) -- */\n"
        "/* a completely foreign, unreferenced placement -- isOKTarget=False, isSwapTarget=False */\n"
        "#97=SHAPE_REPRESENTATION('child_placement_rep',(),#101);\n"
        "#90=CARTESIAN_POINT('ax2_foreign_origin',(200.0,200.0,200.0));\n"
        "#91=AXIS2_PLACEMENT_3D('Ax2_Target_foreign',#90,#2,#3);\n"
        "/* ---- NAUO: Parent relating, Child related ---- */\n"
        "#92=NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','','uses',#45,#87,$);\n"
        "#93=PRODUCT_DEFINITION_SHAPE('Placement','Placement of an item',#92);\n"
        "/* DEFECT: SRRWT relates the two PLACEMENT-ONLY reps; Ax1 genuinely belongs to Rep1 */\n"
        "/* (parent_placement_rep), but Ax2 belongs to NEITHER Rep1 nor Rep2 (child_placement_rep) */\n"
        "#94=ITEM_DEFINED_TRANSFORMATION('','',#60,#91);\n"
        "#95=SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION('srrwt','',#48,#97,#94);\n"
        "#96=CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#95,#93);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_a120(path) -> None:
    Path(path).write_text(_render_a120())


f.render = _render_a120  # type: ignore[method-assign]
f.write = _write_a120    # type: ignore[method-assign]
