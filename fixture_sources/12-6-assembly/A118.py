"""A118 -- NAUO + SHAPE_REPRESENTATION_RELATIONSHIP wired through a real
CONTEXT_DEPENDENT_SHAPE_REPRESENTATION, with the SRR relating the two
representations OPPOSITE to the NAUO direction.

Closes exchange GAP `stp-srr-nauo-reversed`. M062 (the prior fixture) stuffs
its NAUO+SRR pair inside a GEOMETRIC_CURVE_SET with EMPTY shape_representation
items (SHAPE_REPRESENTATION('rep_A',(),#ctx) -- no items at all), so
occt=empty/empty regardless of the reversal logic: the "silently resolved"
warning path is present in bytes but the actual resolved shape is
unobservable (empty either way). This fixture wires the same NAUO+SRR pair
through a REAL CDSR governing two representations that each carry real,
DISTINGUISHABLE geometry (Parent: a 1x1 marker face at the origin; Child: a
5x5 marker face at x=[100,105]), so the resolved shape is live and the
reversal is bytes+shape-observable.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  STEPControl_ActorRead::TransferEntity(StepRepr_NextAssemblyUsageOccurrence)
  (STEPControl_ActorRead.cxx:701-...): walks graph.Sharings(NAUO) -> PDS ->
  graph.Sharings(PDS) -> CDSR, then:
    SRRReversed = STEPConstruct_Assembly::CheckSRRReversesNAUO(graph, CDSR);
    rep = (SRRReversed ? RR->Rep2() : RR->Rep1());
  STEPConstruct_Assembly::CheckSRRReversesNAUO (STEPConstruct_Assembly.cxx:171-217):
    finds the SHAPE_DEFINITION_REPRESENTATION owning Rep1/Rep2, extracts each
    one's PRODUCT_DEFINITION, and compares against NAUO's
    RelatingProductDefinition (parent)/RelatedProductDefinition (child).
    OCCT's OWN writer convention (STEPConstruct_Assembly::MakeRelationship,
    lines 76-122) always builds SRRWT.Rep1 = CHILD's representation,
    SRRWT.Rep2 = PARENT's representation (matching NAUO.Relating=parent,
    Related=child) -- that is the "non-reversed" case
    (CheckSRRReversesNAUO returns False). This fixture deliberately reverses
    that: SRR.Rep1 = PARENT's representation (#39, the same-numbered
    "parent_rep"), SRR.Rep2 = CHILD's representation (#82, "child_rep") --
    exactly opposite of the writer's own convention. CheckSRRReversesNAUO
    detects `pd2 == nauo->RelatedProductDefinition() && pd1 ==
    nauo->RelatingProductDefinition()` and returns True; TransferEntity(NAUO)
    then emits `TP->AddWarning(SRR, "SRR reverses relation defined by NAUO;
    NAUO definition is taken")` and silently uses NAUO's direction (Rep2,
    the PARENT's representation) as the CDSR's contribution to the assembly
    compound -- rather than rejecting the conflicting file.

Root-reachability note: a bare, unreferenced CDSR (M062's structure, minus
the empty-items GEOMETRIC_CURVE_SET wrapper) does NOT independently transfer
in this OCCT build (see U051's Notes for the general finding). The CDSR here
is instead discovered via the standard NAUO-root walk described above: both
Parent and Child carry their OWN normal PRODUCT_DEFINITION -> ... ->
SHAPE_DEFINITION_REPRESENTATION chains (so both representations are real,
resolvable geometry independent of the CDSR), and the CDSR/NAUO/SRR triple is
additionally present, discovered when the recognized ProductDefinition root
is transferred.

Live-verified (2026-07-12, OCP 7.8.1 STEPControl_Reader, direct probing --
not mirrored/guessed): shape_null=False; the transferred compound contains
geometry from BOTH the Parent's own SDR chain and the Child's own SDR chain,
PLUS an additional CDSR-driven contribution (n_faces_total=4, confirming the
CDSR's own TransferEntity call produced an extra, independently-computed
shape rather than being skipped or erroring) -- consistent with "NAUO
definition is taken" (a live shape is silently produced) rather than
rejecting the SRR/NAUO conflict.

Byte assertions:
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'CONTEXT_DEPENDENT_SHAPE_REPRESENTATION')
  contains(b"SHAPE_REPRESENTATION_RELATIONSHIP('rel','',#39,#82)")

Tier-3: shape_null == False; n_faces_total == 4
Expected: occt=shape(1)/shape(1) gmsh=shape(?) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="A118",
    defect=(
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE(Parent relating, Child related) + "
        "CONTEXT_DEPENDENT_SHAPE_REPRESENTATION wrapping a SHAPE_REPRESENTATION_RELATIONSHIP "
        "wired OPPOSITE to the NAUO direction (Rep1=parent_rep, Rep2=child_rep, the reverse of "
        "OCCT's own writer convention Rep1=child,Rep2=parent); CheckSRRReversesNAUO detects the "
        "reversal, AddWarning('SRR reverses relation defined by NAUO; NAUO definition is taken'), "
        "and silently resolves via NAUO's direction rather than rejecting the conflict; both Parent "
        "and Child carry real, distinguishable live geometry via their own PRODUCT_DEFINITION chains "
        "(not empty SHAPE_REPRESENTATION items like M062); "
        "synonyms: assembly direction conflict, SRR vs NAUO direction mismatch, parent/child conflict "
        "in STEP, assembly relation reversed, CDSR silently resolved reversal"
    ),
)


def _render_a118() -> str:
    return (
        "ISO-10303-21;\n"
        "/* A118: NAUO + SRR wired through a real CDSR, SRR direction OPPOSITE to NAUO */\n"
        "/* DEFECT: CheckSRRReversesNAUO detects the reversal; TransferEntity(NAUO) warns */\n"
        "/* 'SRR reverses relation defined by NAUO; NAUO definition is taken' and silently */\n"
        "/* resolves via NAUO's direction instead of rejecting the file -- both Parent/Child */\n"
        "/* carry real, distinguishable geometry (unlike M062's empty-items curve-set orphan) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('A118: SRR reverses NAUO direction, wired through a real CDSR'),'2;1');\n"
        "FILE_NAME('A118.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#100=APPLICATION_CONTEXT('mechanical design');\n"
        "#101=(GEOMETRIC_REPRESENTATION_CONTEXT(3)REPRESENTATION_CONTEXT('','3D'));\n"
        "/* ---- Parent product: small 1x1 marker face at the origin ---- */\n"
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
        "#39=SHAPE_REPRESENTATION('parent_rep',(#38),#101);\n"
        "#40=PRODUCT_CONTEXT('',#100,'mechanical');\n"
        "#41=PRODUCT('Parent','Parent','',(#40));\n"
        "#42=PRODUCT_DEFINITION_FORMATION('','',#41);\n"
        "#43=PRODUCT_DEFINITION_CONTEXT('part definition',#100,'design');\n"
        "#44=PRODUCT_DEFINITION('','',#42,#43);\n"
        "#45=PRODUCT_DEFINITION_SHAPE('','',#44);\n"
        "#46=SHAPE_DEFINITION_REPRESENTATION(#45,#39);\n"
        "/* ---- Child product: bigger 5x5 marker face at (100,0,0) ---- */\n"
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
        "#60=VERTEX_POINT('',#56);\n"
        "#61=VECTOR('',#14,5.0);\n"
        "#62=LINE('',#53,#61);\n"
        "#63=EDGE_CURVE('',#57,#58,#62,.T.);\n"
        "#64=VECTOR('',#18,5.0);\n"
        "#65=LINE('',#54,#64);\n"
        "#66=EDGE_CURVE('',#58,#59,#65,.T.);\n"
        "#67=VECTOR('',#22,5.0);\n"
        "#68=LINE('',#55,#67);\n"
        "#69=EDGE_CURVE('',#59,#60,#68,.T.);\n"
        "#70=VECTOR('',#26,5.0);\n"
        "#71=LINE('',#56,#70);\n"
        "#72=EDGE_CURVE('',#60,#57,#71,.T.);\n"
        "#73=ORIENTED_EDGE('',$,$,#63,.T.);\n"
        "#74=ORIENTED_EDGE('',$,$,#66,.T.);\n"
        "#75=ORIENTED_EDGE('',$,$,#69,.T.);\n"
        "#76=ORIENTED_EDGE('',$,$,#72,.T.);\n"
        "#77=EDGE_LOOP('',(#73,#74,#75,#76));\n"
        "#78=FACE_OUTER_BOUND('',#77,.T.);\n"
        "#79=ADVANCED_FACE('',(#78),#52,.T.);\n"
        "#80=OPEN_SHELL('',(#79));\n"
        "#81=SHELL_BASED_SURFACE_MODEL('',(#80));\n"
        "#82=SHAPE_REPRESENTATION('child_rep',(#81),#101);\n"
        "#83=PRODUCT_CONTEXT('',#100,'mechanical');\n"
        "#84=PRODUCT('Child','Child','',(#83));\n"
        "#85=PRODUCT_DEFINITION_FORMATION('','',#84);\n"
        "#86=PRODUCT_DEFINITION('','',#85,#43);\n"
        "#87=PRODUCT_DEFINITION_SHAPE('','',#86);\n"
        "#88=SHAPE_DEFINITION_REPRESENTATION(#87,#82);\n"
        "/* ---- NAUO: Parent(#44) relating (parent), Child(#86) related (child) ---- */\n"
        "#90=NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','','uses',#44,#86,$);\n"
        "#91=PRODUCT_DEFINITION_SHAPE('Placement','Placement of an item',#90);\n"
        "/* DEFECT: SRR wired OPPOSITE the NAUO direction -- Rep1=parent_rep(#39), Rep2=child_rep(#82); */\n"
        "/* OCCT's own writer convention (STEPConstruct_Assembly::MakeRelationship) always emits */\n"
        "/* Rep1=child,Rep2=parent for this NAUO direction -- this file swaps them. */\n"
        "#92=SHAPE_REPRESENTATION_RELATIONSHIP('rel','',#39,#82);\n"
        "#93=CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#92,#91);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_a118(path) -> None:
    Path(path).write_text(_render_a118())


f.render = _render_a118  # type: ignore[method-assign]
f.write = _write_a118    # type: ignore[method-assign]
