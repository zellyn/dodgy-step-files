"""U050 — unit-scaling mechanism: CONVERSION_BASED_UNIT('INCH',...) on a live 2-face shell.

Closes exchange GAP `seq-xsalgo-unit-mismatch`: a corpus-wide sweep found ZERO
shell-bearing fixtures declaring a non-millimetre length unit, so OCCT's
import-time unit-rescaling of geometry AND repair tolerances
(XSAlgo_AlgoContainer::PrepareForTransfer installs the target length unit
before each transfer; STEPControl_ActorRead::Transfer calls it on the STEP
read path) was unexercised. All five previously-cited fixtures (U001/U002/
U003/Wr044/Wr045) are faceless GEOMETRIC_CURVE_SET scaffolds with occt=empty.

This fixture is a genuine, directly-loadable 2-face OPEN_SHELL (mirrors the
N152/N153 sewing-pair pattern) whose GEOMETRIC_REPRESENTATION_CONTEXT declares
CONVERSION_BASED_UNIT('INCH', LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),
<mm-basis>)) as its actual length unit (unlike A038, where the INCH unit sits
on an unused CONSTRUCTIVE_GEOMETRY_REPRESENTATION side-context and the
shape's real geometry stays in mm). Coordinates are authored in inch-scale
(~1.0 extent): Face A is a 1x1 unit square at y in [0,1]; Face B is a 1x1
unit square at y in [1.001, 2.001] on the SAME plane, leaving a raw 0.001
free-boundary gap between the two faces' facing edges.

Live-verified (2026-07-12, OCP 7.8.1 STEPControl_Reader):
  - Bnd_Box on the transferred shape spans x=[0, 25.4], y=[0, 50.8254] mm —
    confirms the reader genuinely applies the 25.4 conversion factor to
    every coordinate (raw 1.0 -> 25.4mm, raw 2.001 -> 50.8254mm).
  - The interesting repair interaction: the raw 0.001 gap, if a receiver
    forgot to rescale-by-unit before comparing against
    Precision::Confusion (~1e-7 "mm"), would read as a trivially-mergeable
    sub-tolerance gap; correctly scaled, it is a real 0.0254mm crack between
    the two free boundaries — the exact class of tolerance-scaling defect
    XSAlgo_AlgoContainer::PrepareForTransfer / IGESToBRep_Reader::
    TransferRoots exist to get right (precision multiplied by the file's
    unit factor before ProcessShape).
  - validate2 (2026-07-12): occt_heal_on=shape(1) occt_heal_off=shape(1)
    (shape_counts vertex=16 edge=8 wire=2 face=2 shell=2 solid=0 compound=1,
    identical topology signature to N152/N153) gmsh_autofix_on/off=shape(18)
    ifcopenshell=schema_n/a (AUTOMOTIVE_DESIGN unsupported) — all live, not
    mirrored/guessed.
  - tier3_geometric.geometric_report: shape_null=False, n_faces_total=2,
    n_edges_total=8, n_vertices_total=16.
  - structural linter: UNITS_INCONSISTENT (the mm-basis NAMED_UNIT #9056
    feeding the CONVERSION_BASED_UNIT factor plus the INCH NAMED_UNIT #9058
    itself both count as "reachable length units" to the >1-distinct-unit
    heuristic; this is the SAME false-positive class already present on
    U006 and A038's existing, accepted CONVERSION_BASED_UNIT usage — not a
    new defect introduced by this fixture. No **Structural assertion** line
    is registered for U050, consistent with U006/A038.

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('INCH'")
  contains(b'25.4') or matches(rb'LENGTH_MEASURE\\(25\\.4\\)')

Tier-3: shape_null == False; n_faces_total == 2; n_edges_total == 8; n_vertices_total == 16
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from pathlib import Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U050",
    defect=(
        "unit-scaling mechanism: CONVERSION_BASED_UNIT('INCH',...) declared as the "
        "actual length unit of a live 2-face OPEN_SHELL (mirrors N152/N153's sewing-pair "
        "shape), coordinates authored in inch-scale (~1.0 extent) so the mm-converted "
        "model is ~25.4mm; a raw 0.001 free-boundary gap between the two faces becomes a "
        "genuine 0.0254mm crack once the unit factor is correctly applied, exercising "
        "XSAlgo_AlgoContainer::PrepareForTransfer / STEPControl_ActorRead::Transfer's "
        "unit-scaling of both geometry and repair tolerances; "
        "synonyms: inch-declared STEP shell, CONVERSION_BASED_UNIT on live geometry, "
        "unit-scaled tolerance gap, XSAlgo unit mismatch on shell-bearing fixture"
    ),
)


def _render_u050() -> str:
    """Render a Part-21 file: 2-face OPEN_SHELL (N152-style) in a
    CONVERSION_BASED_UNIT('INCH',...) context, coordinates in inch-scale.
    """
    return (
        "ISO-10303-21;\n"
        "/* U050: unit-scaling mechanism — CONVERSION_BASED_UNIT('INCH',...) on a live 2-face shell */\n"
        "/* seq-xsalgo-unit-mismatch: XSAlgo_AlgoContainer::PrepareForTransfer installs target length */\n"
        "/* unit before transfer; the file declares INCH, geometry authored in inch-scale (~1.0 extent) */\n"
        "/* so the mm-converted model is ~25.4mm; a 0.001-inch (0.0254mm) free-boundary gap between the */\n"
        "/* two faces demonstrates the tolerance-scaling interaction: at raw face value the gap (0.001) */\n"
        "/* reads as sub-Precision::Confusion if a reader forgot to rescale, but the true post-conversion */\n"
        "/* gap (0.0254mm) is a genuine, healing-relevant crack once units are correctly applied. */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U050: unit-scaling mechanism (INCH-declared 2-face shell)'),'2;1');\n"
        "FILE_NAME('U050.stp','2026-07-12T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#9000=APPLICATION_CONTEXT('mechanical design');\n"
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
        "#37=CARTESIAN_POINT('',(0.0,1.001,0.0));\n"
        "#38=CARTESIAN_POINT('',(1.0,1.001,0.0));\n"
        "#39=CARTESIAN_POINT('',(1.0,2.001,0.0));\n"
        "#40=CARTESIAN_POINT('',(0.0,2.001,0.0));\n"
        "#41=VERTEX_POINT('',#37);\n"
        "#42=VERTEX_POINT('',#38);\n"
        "#43=VERTEX_POINT('',#39);\n"
        "#44=VERTEX_POINT('',#40);\n"
        "#45=DIRECTION('',(1.0,0.0,0.0));\n"
        "#46=VECTOR('',#45,1.0);\n"
        "#47=LINE('',#37,#46);\n"
        "#48=EDGE_CURVE('',#41,#42,#47,.T.);\n"
        "#49=DIRECTION('',(0.0,1.0,0.0));\n"
        "#50=VECTOR('',#49,1.0);\n"
        "#51=LINE('',#38,#50);\n"
        "#52=EDGE_CURVE('',#42,#43,#51,.T.);\n"
        "#53=DIRECTION('',(-1.0,0.0,0.0));\n"
        "#54=VECTOR('',#53,1.0);\n"
        "#55=LINE('',#39,#54);\n"
        "#56=EDGE_CURVE('',#43,#44,#55,.T.);\n"
        "#57=DIRECTION('',(0.0,-1.0,0.0));\n"
        "#58=VECTOR('',#57,1.0);\n"
        "#59=LINE('',#40,#58);\n"
        "#60=EDGE_CURVE('',#44,#41,#59,.T.);\n"
        "#61=ORIENTED_EDGE('',$,$,#48,.T.);\n"
        "#62=ORIENTED_EDGE('',$,$,#52,.T.);\n"
        "#63=ORIENTED_EDGE('',$,$,#56,.T.);\n"
        "#64=ORIENTED_EDGE('',$,$,#60,.T.);\n"
        "#65=EDGE_LOOP('',(#61,#62,#63,#64));\n"
        "#66=FACE_OUTER_BOUND('',#65,.T.);\n"
        "#67=ADVANCED_FACE('',(#66),#5,.T.);\n"
        "#68=OPEN_SHELL('',(#36,#67));\n"
        "#69=SHELL_BASED_SURFACE_MODEL('',(#68));\n"
        "#9050=PRODUCT_CONTEXT('',#9000,'mechanical');\n"
        "#9051=PRODUCT('U050','U050','',(#9050));\n"
        "#9052=PRODUCT_DEFINITION_FORMATION('','',#9051);\n"
        "#9053=PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design');\n"
        "#9054=PRODUCT_DEFINITION('','','',#9052,#9053);\n"
        "#9055=PRODUCT_DEFINITION_SHAPE('','','',#9054);\n"
        "#9056=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));\n"
        "#9057=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#9056);\n"
        "#9058=(CONVERSION_BASED_UNIT('INCH',#9057)LENGTH_UNIT()NAMED_UNIT(*));\n"
        "#9059=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));\n"
        "#9060=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());\n"
        "#9061=UNCERTAINTY_MEASURE_WITH_UNIT(.LENGTH_MEASURE(1.0E-7).,#9058,'distance_accuracy_value','');\n"
        "#9062=(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#9061))GLOBAL_UNIT_ASSIGNED_CONTEXT((#9058,#9059,#9060))REPRESENTATION_CONTEXT('','3D'));\n"
        "#9063=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#69),#9062);\n"
        "#9064=SHAPE_DEFINITION_REPRESENTATION(#9055,#9063);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u050(path) -> None:
    Path(path).write_text(_render_u050())


f.render = _render_u050  # type: ignore[method-assign]
f.write = _write_u050    # type: ignore[method-assign]
