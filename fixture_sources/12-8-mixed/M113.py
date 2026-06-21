"""M113 — AP209 element_representation with degenerate jacobian (collapsed corner).

Catalog claim: A linear hex's eight corner nodes include two that are
geometrically coincident (n7 == n8). The element collapses to a
prism-shaped degenerate; jacobian determinant is zero at the collapsed
corner. Solver either skips the element or returns NaN stresses.

Reproducer recipe: A VOLUME_3D_ELEMENT_DESCRIPTOR whose 7th and 8th
node references point to two NODE entities with identical coordinates.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M113",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 VOLUME_3D_ELEMENT_DESCRIPTOR for a linear "
        "hex element whose 7th and 8th corner nodes are geometrically coincident; "
        "input: AP209 STEP file where a linear hexahedral element has eight corner NODE "
        "references, but nodes n7 and n8 share identical coordinates (100.0, 100.0, 0.0); "
        "the element collapses from a proper hexahedron to a degenerate prism shape; "
        "per ISO 10303-209 §6 element shape-function jacobian positivity requirement, "
        "the jacobian determinant of the isoparametric mapping must be strictly positive "
        "at all Gauss points; at the collapsed corner the jacobian determinant is zero; "
        "the stiffness matrix for this element is singular; the solver either skips the "
        "element entirely or returns NaN stresses at the collapsed corner integration point; "
        "kernel must detect collapsed corner; reject the element or auto-collapse to a "
        "wedge/prism element with diagnostic; "
        "synonyms: degenerate jacobian, AP209 zero-volume element, FEM hex with coincident "
        "nodes, AP209 collapsed hex element, FEM jacobian zero, degenerate hex"
    ),
    schema="AP242",
)


def _render_m113() -> str:
    """Render AP209 file with VOLUME_3D_ELEMENT_DESCRIPTOR where nodes n7 and n8 are coincident.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#107 CARTESIAN_POINTs for 8 hex corners (n7==n8 coincident — DEFECT)
      #110-#117 NODE entities for each corner
      #300      NODE_GROUP containing all 8 nodes
      #310      FEA_MODEL referencing the node group
      #400      VOLUME_3D_ELEMENT_DESCRIPTOR (hex8) referencing all 8 nodes
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M113: AP209 hex element with degenerate jacobian (collapsed corner) */")
    lines.append("/* DEFECT: nodes n7 and n8 are coincident — hex collapses to prism */")
    lines.append("/* Jacobian determinant is zero at collapsed corner — NaN stresses */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M113: AP209 degenerate hex — coincident nodes n7 n8'),'2;1');")
    lines.append("FILE_NAME('M113.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Hex corner nodes: n1-n6 normal, n7 and n8 COINCIDENT — the defect */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(100.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(100.0,100.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(0.0,100.0,0.0));")
    lines.append("#104=CARTESIAN_POINT('n5',(0.0,0.0,100.0));")
    lines.append("#105=CARTESIAN_POINT('n6',(100.0,0.0,100.0));")
    lines.append("/* DEFECT: n7 and n8 share identical coordinates — jacobian det = 0 at this corner */")
    lines.append("#106=CARTESIAN_POINT('n7',(100.0,100.0,0.0));")
    lines.append("#107=CARTESIAN_POINT('n8',(100.0,100.0,0.0));")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("#111=NODE('n2',(#101),$);")
    lines.append("#112=NODE('n3',(#102),$);")
    lines.append("#113=NODE('n4',(#103),$);")
    lines.append("#114=NODE('n5',(#104),$);")
    lines.append("#115=NODE('n6',(#105),$);")
    lines.append("#116=NODE('n7',(#106),$);")
    lines.append("#117=NODE('n8',(#107),$);")
    lines.append("/* NODE_GROUP containing all eight corner nodes */")
    lines.append("#300=NODE_GROUP('hex_nodes',(#110,#111,#112,#113,#114,#115,#116,#117),$);")
    lines.append("#310=FEA_MODEL('hex_model',$,'',(#300),(),());")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* DEFECT: hex8 element — n7 (#116) and n8 (#117) are coincident */")
    lines.append("/* Isoparametric jacobian is singular at collapsed corner */")
    lines.append("#400=VOLUME_3D_ELEMENT_DESCRIPTOR('hex8_degenerate',.HEX.,")
    lines.append("  (#110,#111,#112,#113,#114,#115,#116,#117));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-hex-element-degenerate-jacobian-collapsed-corner',")
    lines.append("  (#110,#111,#112,#113,#114,#115,#116,#117,#310,#400));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M113','M113','M113',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m113(path) -> None:
    Path(path).write_text(_render_m113())


f.render = _render_m113  # type: ignore[method-assign]
f.write = _write_m113    # type: ignore[method-assign]
