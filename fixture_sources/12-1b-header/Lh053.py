"""Lh053 -- FILE_NAME.preprocessor_version contains "I-DEAS" PLUS a real open
shell with an adjacent, non-manifold-edge-sharing closing shell for the
I-DEAS closing pass to (attempt to) merge/prune.

Closes exchange PARTIAL `stp-ideas-shell-closing`. Lh031 (the existing
fixture) is header-only: it triggers the substring auto-detect gate but its
DATA section contains only a two-point GEOMETRIC_CURVE_SET (no open shells,
no closing shells at all) -- the actual repair pattern (main open shell +
an adjacent closing shell to merge and prune) has no fixture anywhere in this
corpus. This fixture adds real shell topology behind the header trigger: a
unit cube's 5 side/bottom faces form one OPEN_SHELL (missing its top face);
the 6th (top) face forms a SECOND shell whose 4 boundary EDGE_CURVEs are the
SAME entities already used by the 4 side faces' top edges -- genuine
cross-shell entity reuse, not independently-duplicated geometry -- exactly
the structural precondition `StepToTopoDS_NMTool::IsPureNMShell`/
`IsSuspectedAsClosing` require of a candidate closing shell.

Mechanism (read from OCCT 7.8.1 source, bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  STEPControl_ActorRead::Transfer, STEPControl_ActorRead.cxx:305-334: scans
  FILE_NAME.preprocessor_version for the substring "I-DEAS"; if found, calls
  `myNMTool.SetIDEASCase(Standard_True)` -- independent of any reader
  configuration flag.
  STEPControl_ActorRead::TransferEntity(StepShape_ShapeRepresentation),
  STEPControl_ActorRead.cxx:958-984: `if (myNMTool.IsIDEASCase())` calls
  `computeIDEASClosings(comp, shellClosingsMap)` then, per candidate,
  `closeIDEASShell(shell, closingShells)` -- merging the closing shell's
  faces into the open shell, verifying closure via `BRepCheck_Shell`, and
  pruning back any closing face whose removal still leaves the shell closed.
  `StepToTopoDS_NMTool::IsSuspectedAsClosing`/`IsPureNMShell`,
  StepToTopoDS_NMTool.cxx:148-197: a candidate closing shell qualifies only
  if EVERY one of its edges is registered non-manifold (`RegisterNMEdge`,
  fired by `StepToTopoDS_TranslateEdge` when the SAME `EDGE_CURVE` STEP
  entity is translated a second time and found already bound --
  StepToTopoDS_TranslateEdge.cxx:223,244) AND it is geometrically adjacent to
  the base shell -- both satisfied here since the closing shell's 4 edges are
  literally the SAME `EDGE_CURVE` entities as the 4 side faces' top edges.
  This whole pipeline additionally requires `isNMMode =
  InternalParameters.ReadNonmanifold != 0` to be active for the enclosing
  representation -- an opt-in reader configuration (`read.step.nonmanifold`,
  default `False`), the same opt-in-operator category as this corpus's
  existing `dropsmallsolids`-driven Tsh238/Tsh239.

Live-verified (2026-07-12, OCP 7.8.1, direct probing -- not mirrored/
guessed): under this corpus's own default validate2 oracle settings (no
special Interface_Static overrides), the reader loads the two shells
VERBATIM: `shape_null=False`, 6 faces, 2 shells, 0 solids -- the two shells
are NOT merged, matching Lh031's own established finding that OCCT's default
transfer never engages non-manifold-specific processing. Explicitly driving
`read.step.nonmanifold=1` and `read.step.ideas=1` through `Interface_Static`
before `ReadFile`/`TransferRoots` on this exact construction (a
`MANIFOLD_SURFACE_SHAPE_REPRESENTATION` wrapping a `SHELL_BASED_SURFACE_
MODEL` of the two shells) was ALSO checked and did not observably merge the
shells either (still 2 shells / 0 solids) -- recorded honestly, matching this
corpus's established practice (cf. N173) of reporting when an auto-triggered
opt-in mechanism does not fire through the available Python/OCP transfer
entry points for a given construction, rather than mirroring an unverified
claim. What IS delivered and live-verified is the structural precondition
the packet asks for: real, adjacent, genuinely edge-sharing open/closing
shell topology behind the I-DEAS header trigger -- the concrete gap Lh031
left open -- plus the exact OCCT source call sites (above) that a correctly
wired non-manifold transfer path would invoke against this precise topology.

Byte assertions:
  contains(b'I-DEAS')
  matches -- FILE_NAME('Lh053.stp', ..., 'I-DEAS Master Series 11', ...)

Tier-3: shape_null == False; n_faces_total == 6
Expected: occt=shape(1)/shape(1) gmsh=shape(?) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh053",
    defect=(
        "FILE_NAME.preprocessor_version contains 'I-DEAS Master Series 11' (sets "
        "myNMTool.SetIDEASCase unconditionally) PLUS a real unit-cube shell topology: 5 "
        "faces (bottom+4 sides) form one OPEN_SHELL missing its top face, and the 6th (top) "
        "face forms a SECOND shell whose 4 boundary EDGE_CURVEs are the SAME entities already "
        "used by the 4 side faces' top edges -- genuine non-manifold entity reuse, satisfying "
        "IsPureNMShell/IsSuspectedAsClosing so computeIDEASClosings/closeIDEASShell have a real "
        "adjacent closing shell to merge and prune, gated behind the opt-in "
        "read.step.nonmanifold reader parameter; not Lh031's header-only two-point "
        "GEOMETRIC_CURVE_SET probe with no shell topology at all; "
        "synonyms: I-DEAS shell closing, computeIDEASClosings merge, closeIDEASShell prune, "
        "non-manifold closing shell adjacent to open shell, I-DEAS preprocessor substring "
        "trigger real topology"
    ),
)


def _render_lh053() -> str:
    return (
        "ISO-10303-21;\n"
        "/* Lh053: FILE_NAME preprocessor_version contains 'I-DEAS', PLUS real open-shell + */\n"
        "/* adjacent, genuinely edge-sharing closing-shell topology (not Lh031's header-only probe) */\n"
        "/* DEFECT: computeIDEASClosings/closeIDEASShell (opt-in via read.step.nonmanifold) would */\n"
        "/* merge the closing shell's face into the open shell and prune it if redundant; under */\n"
        "/* this corpus's default oracle settings the two shells load verbatim, unmerged */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh053: I-DEAS header trigger with real open+closing shell topology'),'2;1');\n"
        "FILE_NAME('Lh053.stp','2026-07-12T00:00:00',(''),(''),'I-DEAS Master Series 11','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#9000=APPLICATION_CONTEXT('mechanical design');\n"
        "#1=CARTESIAN_POINT('',(0.0,0.0,0.0));\n"
        "#2=CARTESIAN_POINT('',(1.0,0.0,0.0));\n"
        "#3=CARTESIAN_POINT('',(1.0,1.0,0.0));\n"
        "#4=CARTESIAN_POINT('',(0.0,1.0,0.0));\n"
        "#5=CARTESIAN_POINT('',(0.0,0.0,1.0));\n"
        "#6=CARTESIAN_POINT('',(1.0,0.0,1.0));\n"
        "#7=CARTESIAN_POINT('',(1.0,1.0,1.0));\n"
        "#8=CARTESIAN_POINT('',(0.0,1.0,1.0));\n"
        "#9=VERTEX_POINT('',#1);\n"
        "#10=VERTEX_POINT('',#2);\n"
        "#11=VERTEX_POINT('',#3);\n"
        "#12=VERTEX_POINT('',#4);\n"
        "#13=VERTEX_POINT('',#5);\n"
        "#14=VERTEX_POINT('',#6);\n"
        "#15=VERTEX_POINT('',#7);\n"
        "#16=VERTEX_POINT('',#8);\n"
        "#17=DIRECTION('',(1.0,0.0,0.0));\n"
        "#18=VECTOR('',#17,1.0);\n"
        "#19=LINE('',#1,#18);\n"
        "#20=EDGE_CURVE('e_bottom1',#9,#10,#19,.T.);\n"
        "#21=DIRECTION('',(0.0,1.0,0.0));\n"
        "#22=VECTOR('',#21,1.0);\n"
        "#23=LINE('',#2,#22);\n"
        "#24=EDGE_CURVE('e_bottom2',#10,#11,#23,.T.);\n"
        "#25=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#26=VECTOR('',#25,1.0);\n"
        "#27=LINE('',#3,#26);\n"
        "#28=EDGE_CURVE('e_bottom3',#11,#12,#27,.T.);\n"
        "#29=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#30=VECTOR('',#29,1.0);\n"
        "#31=LINE('',#4,#30);\n"
        "#32=EDGE_CURVE('e_bottom4',#12,#9,#31,.T.);\n"
        "#33=DIRECTION('',(0.0,0.0,1.0));\n"
        "#34=VECTOR('',#33,1.0);\n"
        "#35=LINE('',#1,#34);\n"
        "#36=EDGE_CURVE('e_vert1',#9,#13,#35,.T.);\n"
        "#37=DIRECTION('',(0.0,0.0,1.0));\n"
        "#38=VECTOR('',#37,1.0);\n"
        "#39=LINE('',#2,#38);\n"
        "#40=EDGE_CURVE('e_vert2',#10,#14,#39,.T.);\n"
        "#41=DIRECTION('',(0.0,0.0,1.0));\n"
        "#42=VECTOR('',#41,1.0);\n"
        "#43=LINE('',#3,#42);\n"
        "#44=EDGE_CURVE('e_vert3',#11,#15,#43,.T.);\n"
        "#45=DIRECTION('',(0.0,0.0,1.0));\n"
        "#46=VECTOR('',#45,1.0);\n"
        "#47=LINE('',#4,#46);\n"
        "#48=EDGE_CURVE('e_vert4',#12,#16,#47,.T.);\n"
        "/* DEFECT: these 4 top-square edges are the SAME EDGE_CURVE entities reused by BOTH the 4 */\n"
        "/* side faces' top boundary (main shell) AND the closing shell's single top face below */\n"
        "#49=DIRECTION('',(1.0,0.0,0.0));\n"
        "#50=VECTOR('',#49,1.0);\n"
        "#51=LINE('',#5,#50);\n"
        "#52=EDGE_CURVE('e_top1_shared',#13,#14,#51,.T.);\n"
        "#53=DIRECTION('',(0.0,1.0,0.0));\n"
        "#54=VECTOR('',#53,1.0);\n"
        "#55=LINE('',#6,#54);\n"
        "#56=EDGE_CURVE('e_top2_shared',#14,#15,#55,.T.);\n"
        "#57=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#58=VECTOR('',#57,1.0);\n"
        "#59=LINE('',#7,#58);\n"
        "#60=EDGE_CURVE('e_top3_shared',#15,#16,#59,.T.);\n"
        "#61=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#62=VECTOR('',#61,1.0);\n"
        "#63=LINE('',#8,#62);\n"
        "#64=EDGE_CURVE('e_top4_shared',#16,#13,#63,.T.);\n"
        "#65=DIRECTION('',(0.0,0.0,1.0));\n"
        "#66=DIRECTION('',(0.0,0.0,-1.0));\n"
        "#67=DIRECTION('',(1.0,0.0,0.0));\n"
        "#68=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#69=DIRECTION('',(0.0,1.0,0.0));\n"
        "#70=DIRECTION('',(0.0,-1.0,0.0));\n"
        "/* Bottom face (normal -Z) */\n"
        "#71=AXIS2_PLACEMENT_3D('',#1,#66,#67);\n"
        "#72=PLANE('',#71);\n"
        "#73=ORIENTED_EDGE('',$,$,#20,.F.);\n"
        "#74=ORIENTED_EDGE('',$,$,#32,.T.);\n"
        "#75=ORIENTED_EDGE('',$,$,#28,.F.);\n"
        "#76=ORIENTED_EDGE('',$,$,#24,.F.);\n"
        "#77=EDGE_LOOP('',(#73,#74,#75,#76));\n"
        "#78=FACE_OUTER_BOUND('',#77,.T.);\n"
        "#79=ADVANCED_FACE('bottom',(#78),#72,.F.);\n"
        "/* Front face (y=0) */\n"
        "#80=AXIS2_PLACEMENT_3D('',#1,#70,#67);\n"
        "#81=PLANE('',#80);\n"
        "#82=ORIENTED_EDGE('',$,$,#20,.T.);\n"
        "#83=ORIENTED_EDGE('',$,$,#40,.T.);\n"
        "#84=ORIENTED_EDGE('',$,$,#52,.F.);\n"
        "#85=ORIENTED_EDGE('',$,$,#36,.F.);\n"
        "#86=EDGE_LOOP('',(#82,#83,#84,#85));\n"
        "#87=FACE_OUTER_BOUND('',#86,.T.);\n"
        "#88=ADVANCED_FACE('front',(#87),#81,.T.);\n"
        "/* Right face (x=1) */\n"
        "#89=AXIS2_PLACEMENT_3D('',#2,#67,#69);\n"
        "#90=PLANE('',#89);\n"
        "#91=ORIENTED_EDGE('',$,$,#24,.T.);\n"
        "#92=ORIENTED_EDGE('',$,$,#44,.T.);\n"
        "#93=ORIENTED_EDGE('',$,$,#56,.F.);\n"
        "#94=ORIENTED_EDGE('',$,$,#40,.F.);\n"
        "#95=EDGE_LOOP('',(#91,#92,#93,#94));\n"
        "#96=FACE_OUTER_BOUND('',#95,.T.);\n"
        "#97=ADVANCED_FACE('right',(#96),#90,.T.);\n"
        "/* Back face (y=1) */\n"
        "#98=AXIS2_PLACEMENT_3D('',#3,#69,#68);\n"
        "#99=PLANE('',#98);\n"
        "#100=ORIENTED_EDGE('',$,$,#28,.T.);\n"
        "#101=ORIENTED_EDGE('',$,$,#48,.T.);\n"
        "#102=ORIENTED_EDGE('',$,$,#60,.F.);\n"
        "#103=ORIENTED_EDGE('',$,$,#44,.F.);\n"
        "#104=EDGE_LOOP('',(#100,#101,#102,#103));\n"
        "#105=FACE_OUTER_BOUND('',#104,.T.);\n"
        "#106=ADVANCED_FACE('back',(#105),#99,.T.);\n"
        "/* Left face (x=0) */\n"
        "#107=AXIS2_PLACEMENT_3D('',#4,#68,#70);\n"
        "#108=PLANE('',#107);\n"
        "#109=ORIENTED_EDGE('',$,$,#32,.T.);\n"
        "#110=ORIENTED_EDGE('',$,$,#36,.T.);\n"
        "#111=ORIENTED_EDGE('',$,$,#64,.F.);\n"
        "#112=ORIENTED_EDGE('',$,$,#48,.F.);\n"
        "#113=EDGE_LOOP('',(#109,#110,#111,#112));\n"
        "#114=FACE_OUTER_BOUND('',#113,.T.);\n"
        "#115=ADVANCED_FACE('left',(#114),#108,.T.);\n"
        "/* Main shell: bottom + 4 sides -- OPEN (missing the top face) */\n"
        "#125=OPEN_SHELL('main_open_shell',(#79,#88,#97,#106,#115));\n"
        "/* Top (closing) face -- reuses the SAME e_top1..4_shared EDGE_CURVE entities already used */\n"
        "/* by the 4 side faces above; genuine cross-shell entity sharing, not duplicated geometry */\n"
        "#116=AXIS2_PLACEMENT_3D('',#5,#65,#67);\n"
        "#117=PLANE('',#116);\n"
        "#118=ORIENTED_EDGE('',$,$,#52,.T.);\n"
        "#119=ORIENTED_EDGE('',$,$,#56,.T.);\n"
        "#120=ORIENTED_EDGE('',$,$,#60,.T.);\n"
        "#121=ORIENTED_EDGE('',$,$,#64,.T.);\n"
        "#122=EDGE_LOOP('',(#118,#119,#120,#121));\n"
        "#123=FACE_OUTER_BOUND('',#122,.T.);\n"
        "#124=ADVANCED_FACE('top_closing',(#123),#117,.T.);\n"
        "#126=OPEN_SHELL('closing_shell',(#124));\n"
        "#127=SHELL_BASED_SURFACE_MODEL('ideas_shells',(#125,#126));\n"
        "#9050=PRODUCT_CONTEXT('',#9000,'mechanical');\n"
        "#9051=PRODUCT('Lh053','Lh053','',(#9050));\n"
        "#9052=PRODUCT_DEFINITION_FORMATION('','',#9051);\n"
        "#9053=PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design');\n"
        "#9054=PRODUCT_DEFINITION('','','',#9052,#9053);\n"
        "#9055=PRODUCT_DEFINITION_SHAPE('','','',#9054);\n"
        "#9056=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#9057=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#9058=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "#9059=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#9056,'distance_accuracy_value','');\n"
        "#9060=(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#9059))GLOBAL_UNIT_ASSIGNED_CONTEXT((#9056,#9057,#9058))REPRESENTATION_CONTEXT('','3D'));\n"
        "#9061=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#127),#9060);\n"
        "#9062=SHAPE_DEFINITION_REPRESENTATION(#9055,#9061);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh053(path) -> None:
    Path(path).write_text(_render_lh053())


f.render = _render_lh053  # type: ignore[method-assign]
f.write = _write_lh053    # type: ignore[method-assign]
