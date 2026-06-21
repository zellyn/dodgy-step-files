"""M114 — AP209 hex element with aspect ratio greater than 10000.

Catalog claim: A linear hex element has dimensions 1000.0 × 0.1 × 0.1 (mm).
Aspect ratio is 10000:1. Stiffness matrix is severely ill-conditioned;
bending stresses diverge from any analytical reference.

Reproducer recipe: A VOLUME_3D_ELEMENT_DESCRIPTOR with corner node
coordinates spanning 1000mm in X but 0.1mm in Y and Z.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M114",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 VOLUME_3D_ELEMENT_DESCRIPTOR for a linear "
        "hex element with an extreme aspect ratio of 10000:1 (1000.0mm × 0.1mm × 0.1mm); "
        "input: AP209 STEP file where a linear hexahedral element has eight corner NODE "
        "coordinates spanning 1000.0 mm in the X direction but only 0.1 mm in both Y and Z; "
        "the resulting aspect ratio is 1000.0 / 0.1 = 10000, far exceeding the mesh quality "
        "thresholds recommended in AP209 §6 element shape-quality guidelines and the "
        "Abaqus/Ansys mesh-quality thresholds (typically aspect ratio < 10); "
        "the stiffness matrix for this ribbon hex is severely ill-conditioned; the condition "
        "number is proportional to aspect_ratio^2 ≈ 1e8, causing bending stresses to diverge "
        "from any analytical reference solution; iterative solvers may fail to converge; "
        "direct solvers return results with large floating-point errors; "
        "kernel must warn on aspect-ratio outliers above threshold and let user opt to keep "
        "or reject the element; "
        "synonyms: sliver element, AP209 thin hex, high aspect ratio, AP209 sliver element, "
        "FEM hex aspect ratio enormous, extremely thin hexahedron"
    ),
    schema="AP242",
)


def _render_m114() -> str:
    """Render AP209 file with VOLUME_3D_ELEMENT_DESCRIPTOR for a 10000:1 aspect ratio hex.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#107 CARTESIAN_POINTs: X spans 0..1000mm, Y/Z only 0..0.1mm
      #110-#117 NODE entities for each corner
      #300      NODE_GROUP containing all 8 nodes
      #310      FEA_MODEL referencing the node group
      #400      VOLUME_3D_ELEMENT_DESCRIPTOR (hex8) — aspect ratio 10000:1
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M114: AP209 hex element with extreme aspect ratio 10000:1 */")
    lines.append("/* DEFECT: hex spans 1000mm in X but only 0.1mm in Y and Z */")
    lines.append("/* Stiffness matrix ill-conditioned; bending stresses diverge */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M114: AP209 sliver hex element aspect ratio 10000:1'),'2;1');")
    lines.append("FILE_NAME('M114.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Ribbon hex corners: 1000mm in X, only 0.1mm in Y and Z — aspect ratio 10000:1 */")
    lines.append("/* Bottom face (z=0.0) */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(1000.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(1000.0,0.1,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(0.0,0.1,0.0));")
    lines.append("/* Top face (z=0.1mm) — making the hex 1000mm × 0.1mm × 0.1mm */")
    lines.append("#104=CARTESIAN_POINT('n5',(0.0,0.0,0.1));")
    lines.append("#105=CARTESIAN_POINT('n6',(1000.0,0.0,0.1));")
    lines.append("#106=CARTESIAN_POINT('n7',(1000.0,0.1,0.1));")
    lines.append("#107=CARTESIAN_POINT('n8',(0.0,0.1,0.1));")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("#111=NODE('n2',(#101),$);")
    lines.append("#112=NODE('n3',(#102),$);")
    lines.append("#113=NODE('n4',(#103),$);")
    lines.append("#114=NODE('n5',(#104),$);")
    lines.append("#115=NODE('n6',(#105),$);")
    lines.append("#116=NODE('n7',(#106),$);")
    lines.append("#117=NODE('n8',(#107),$);")
    lines.append("/* NODE_GROUP containing all eight corner nodes */")
    lines.append("#300=NODE_GROUP('sliver_nodes',(#110,#111,#112,#113,#114,#115,#116,#117),$);")
    lines.append("#310=FEA_MODEL('sliver_model',$,'',(#300),(),());")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* DEFECT: hex8 with aspect ratio 10000:1 — 1000mm × 0.1mm × 0.1mm ribbon */")
    lines.append("/* Stiffness matrix condition number ≈ aspect_ratio^2 = 1e8; solver ill-conditioned */")
    lines.append("#400=VOLUME_3D_ELEMENT_DESCRIPTOR('hex8_sliver',.HEX.,")
    lines.append("  (#110,#111,#112,#113,#114,#115,#116,#117));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-hex-element-aspect-ratio-greater-than-10000',")
    lines.append("  (#110,#111,#112,#113,#114,#115,#116,#117,#310,#400));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M114','M114','M114',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m114(path) -> None:
    Path(path).write_text(_render_m114())


f.render = _render_m114  # type: ignore[method-assign]
f.write = _write_m114    # type: ignore[method-assign]
