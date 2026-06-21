"""M116 — AP209 modal extraction count exceeds DOF rank.

Catalog claim: A modal-analysis card requests extraction of 50 modes from
a model with only 18 active DOFs (three free nodes × 6 DOFs each = 18,
or three free nodes × 3 translational DOFs = 9). The eigensolver either
returns real modes plus NaN/garbage entries, or fails outright.

Reproducer recipe: A FEA_MODEL_3D with three free nodes (9 DOFs) but a
modal extraction parameter requesting 50 modes.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'FEA_MODEL')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M116",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 FEA_MODEL with a modal extraction parameter "
        "requesting 50 modes from a model with only 9 active translational DOFs; "
        "input: AP209 STEP file where a FEA_MODEL contains three free NODE entities "
        "(9 translational DOFs total: 3 nodes × 3 DOF each) but the modal analysis "
        "configuration specifies REQUESTED_NUMBER_OF_MODES = 50; "
        "per ISO 10303-209 §9 eigenvalue_extraction_method requested-mode count vs system "
        "DOF invariant, the number of requested modes cannot exceed the system DOF rank; "
        "requesting 50 modes from a 9-DOF system forces the eigensolver to attempt to "
        "extract 41 additional modes beyond the system rank; the eigensolver either returns "
        "9 real modes plus 41 NaN/garbage eigenvalue entries, or fails outright with a "
        "rank-deficiency error; downstream stress recovery using the spurious modes produces "
        "meaningless results; "
        "kernel must heal and accept: coerce the requested mode count to the system rank "
        "and warn loudly; "
        "synonyms: AP209 mode count too high, eigensolver over-request, modal extraction "
        "count exceeds DOF rank, more modes than DOFs, AP209 NaN modes returned, "
        "AP209 too many modes requested, FEM eigensolver returns NaN modes, "
        "mode count exceeds DOF"
    ),
    schema="AP242",
)


def _render_m116() -> str:
    """Render AP209 file with FEA_MODEL requesting 50 modes but only 9 DOFs available.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#102 CARTESIAN_POINTs for three free nodes
      #110-#112 NODE entities (3 nodes × 3 translational DOF = 9 DOFs)
      #300      NODE_GROUP containing all three nodes
      #310      FEA_MODEL referencing the node group
      #400      Modal analysis parameter: REQUESTED_NUMBER_OF_MODES = 50 — DEFECT
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M116: AP209 modal extraction count exceeds DOF rank */")
    lines.append("/* DEFECT: 50 modes requested from a model with only 9 active DOFs */")
    lines.append("/* Eigensolver returns NaN/garbage for 41 modes beyond system rank */")
    lines.append("/* Per AP209 §9, requested mode count must not exceed DOF rank */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'FEA_MODEL') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M116: AP209 modal extraction requests 50 modes from 9-DOF model'),'2;1');")
    lines.append("FILE_NAME('M116.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('fea','3D'));")
    lines.append("/* Three free nodes: total 9 translational DOFs (3 nodes × 3 DOF each) */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(50.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(100.0,0.0,0.0));")
    lines.append("#110=NODE('free_node_1',(#100),$);")
    lines.append("#111=NODE('free_node_2',(#101),$);")
    lines.append("#112=NODE('free_node_3',(#102),$);")
    lines.append("/* Byte assertion: contains(b'FEA_MODEL') */")
    lines.append("/* NODE_GROUP: all three free nodes — 9 translational DOFs total */")
    lines.append("#300=NODE_GROUP('free_nodes',(#110,#111,#112),$);")
    lines.append("#310=FEA_MODEL('modal_model',$,'',(#300),(),());")
    lines.append("/* DEFECT: modal analysis requests 50 modes from a 9-DOF system *)  */")
    lines.append("/* Eigensolver can return at most 9 real modes; modes 10-50 are NaN/garbage *)  */")
    lines.append("/* REQUESTED_NUMBER_OF_MODES = 50 >> system DOF rank = 9 *)  */")
    lines.append("#400=EIGENVALUE_EXTRACTION_PARAMETER('modal_50','LANCZOS',50,0.0,$,#310);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-modal-extraction-count-exceeds-dof-rank',")
    lines.append("  (#110,#111,#112,#310,#400));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M116','M116','M116',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m116(path) -> None:
    Path(path).write_text(_render_m116())


f.render = _render_m116  # type: ignore[method-assign]
f.write = _write_m116    # type: ignore[method-assign]
