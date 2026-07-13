"""U051 -- SHAPE_REPRESENTATION.context_of_items = $ (null) directly governing a live shell.

Closes exchange GAP `stp-missing-unit-context-default` subvariant (a): "entity with
no unit context reachable through the graph -> default units" (occt-coverage/
exchange/problems.json). M063 (the prior fixture for this class) hosts its
no-unit SHAPE_REPRESENTATION inside a GEOMETRIC_CURVE_SET, which is not a
GeometricRepresentationItem -- StepToTopoDS's item-dispatch silently
type-skips it, so M063's shape(1) comes from an outer, correctly-unitted
representation and the no-unit-context fallback never actually runs
(COVERED_FULL_REVERIFY.md downgraded this class COVERED->GAP for exactly this
reason). This fixture fixes that: the SHAPE_REPRESENTATION with the missing
context directly wraps a live ADVANCED_FACE/OPEN_SHELL/SHELL_BASED_SURFACE_MODEL
-- a genuine GeometricRepresentationItem chain, not a curve-set escape hatch.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  STEPControl_ActorRead::PrepareUnits (STEPControl_ActorRead.cxx:1784-1802):
    Handle(StepRepr_RepresentationContext) theRepCont = rep->ContextOfItems();
    if (theRepCont.IsNull()) {
      TP->AddWarning(rep,"Bad RepresentationContext, default unit taken");
      ResetUnits(aModel, theLocalFactors);
      return;
    }
  This fixture's SHAPE_REPRESENTATION('no_context_shape',(#shell),$) sets the
  4th SHAPE_REPRESENTATION attribute (context_of_items) to $ -- a genuinely
  ABSENT context, the literal "no unit context reachable" case (distinct from
  U052's sibling subvariant, where a context entity IS present but is the
  wrong kind).

Root-reachability note (live-verified 2026-07-12, OCP 7.8.1): a completely
bare, unreferenced FACE_SURFACE/SHELL_BASED_SURFACE_MODEL with NO enclosing
PRODUCT_DEFINITION chain does NOT get picked up by STEPControl_Reader.
TransferRoots() at all in this OCCT build (NbRootsForTransfer()==0, confirmed
via direct OCP probing: STEPControl_ActorRead::Recognize() gates FaceSurface/
ShellBasedSurfaceModel/MappedItem/ContextDependentShapeRepresentation behind a
model-bound check that a bare, product-chain-less root never satisfies in
practice). So "no SHAPE_REPRESENTATION reachable at ALL" (the packet's most
literal phrasing of item 1a) is not actually constructible as a live,
transferring fixture -- the corpus's own M063 precedent already needed SOME
enclosing PRODUCT chain to be reachable at all. This fixture instead builds
the closest true-to-mechanism alternative that IS live-reachable: a normal
PRODUCT_DEFINITION -> PRODUCT_DEFINITION_SHAPE -> SHAPE_DEFINITION_REPRESENTATION
chain whose SHAPE_REPRESENTATION itself has context_of_items=$ (the literal
"no context" condition PrepareUnits checks for), directly wrapping live shell
geometry. Live-verified: shape_null=False, n_faces_total=1 (confirmed via
tier3_geometric and direct OCP TransferRoots probing, not mirrored/guessed).

Byte assertions:
  contains(b"SHAPE_REPRESENTATION('no_context_shape'")
  matches -- SHAPE_REPRESENTATION('no_context_shape',(#N),$) literal form

Tier-3: shape_null == False; n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U051",
    defect=(
        "SHAPE_REPRESENTATION.context_of_items = $ (null) directly governing a live "
        "ADVANCED_FACE/OPEN_SHELL/SHELL_BASED_SURFACE_MODEL -- PrepareUnits's "
        "'theRepCont.IsNull()' branch fires ('Bad RepresentationContext, default unit "
        "taken'), reader silently substitutes default units and still returns a live, "
        "non-null shape; not GEOMETRIC_CURVE_SET-hosted like M063 (a real "
        "GeometricRepresentationItem chain, not a type-skipped curve set); "
        "synonyms: STEP no units defaulted, kernel guessed units, model 1000x wrong, "
        "SHAPE_REPRESENTATION context_of_items null, no unit context reachable through "
        "the graph"
    ),
)


def _render_u051() -> str:
    return (
        "ISO-10303-21;\n"
        "/* U051: SHAPE_REPRESENTATION.context_of_items = $ (null), directly governing a live shell */\n"
        "/* DEFECT: PrepareUnits's rep->ContextOfItems().IsNull() branch fires -- */\n"
        "/* 'Bad RepresentationContext, default unit taken' -- reader silently defaults units */\n"
        "/* and still returns a live, non-null shape (not a GEOMETRIC_CURVE_SET type-skip like M063) */\n"
        "/* Byte assertion: literal form SHAPE_REPRESENTATION('no_context_shape',(#N),$) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U051: SHAPE_REPRESENTATION with null context_of_items on a live shell'),'2;1');\n"
        "FILE_NAME('U051.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
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
        "#102=PRODUCT('U051','U051','',(#101));\n"
        "#103=PRODUCT_DEFINITION_FORMATION('','',#102);\n"
        "#104=PRODUCT_DEFINITION_CONTEXT('part definition',#100,'design');\n"
        "#105=PRODUCT_DEFINITION('','',#103,#104);\n"
        "#106=PRODUCT_DEFINITION_SHAPE('','',#105);\n"
        "/* DEFECT: context_of_items = $ (null) -- no unit context reachable for this representation */\n"
        "#107=SHAPE_REPRESENTATION('no_context_shape',(#38),$);\n"
        "#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u051(path) -> None:
    Path(path).write_text(_render_u051())


f.render = _render_u051  # type: ignore[method-assign]
f.write = _write_u051    # type: ignore[method-assign]
