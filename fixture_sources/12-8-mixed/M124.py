"""M124 — AP209 fea_model includes element referencing a node outside its node-set.

Catalog claim: A FEA_MODEL_3D declares a NODE_GROUP of nodes (n1, n2, n3) as
its_node_set and a VOLUME_3D_ELEMENT_DESCRIPTOR referencing nodes (n1, n2, n3,
n4) in its_element_set. Node n4 is outside the model's declared node set.

Reproducer recipe: FEA_MODEL_3D with a 3-node its_node_set and a 4-node tet
element in its_element_set referencing n4 which is not in the node-set.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'FEA_MODEL_3D')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M124",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 FEA_MODEL_3D whose element references "
        "a node (n4) outside the declared node-set (n1, n2, n3); "
        "input: AP209 STEP file where a FEA_MODEL_3D entity declares a NODE_GROUP "
        "of three nodes (n1, n2, n3) as its_node_set and a VOLUME_3D_ELEMENT_DESCRIPTOR "
        "referencing four nodes (n1, n2, n3, n4) in its_element_set; node n4 has a "
        "CARTESIAN_POINT and NODE entity in the file but is not listed in the model's "
        "its_node_set NODE_GROUP; "
        "per ISO 10303-209 §6 fea_model.its_node_set / its_element_set consistency "
        "invariant, every node referenced by any element in its_element_set must be a "
        "member of its_node_set; a node outside the set either silently expands the "
        "active node set (making the model larger than declared) or causes solver "
        "assembly to fail because the global DOF numbering does not include n4; "
        "kernel must validate that all element nodes lie within the model node-set and "
        "reject or auto-expand with diagnostic; "
        "synonyms: AP209 model node-set leak, element outside FEA model, "
        "fea_model node-set inconsistent, element references node not in node_set, "
        "FEM element extends model implicitly, AP209 element refers to outside node"
    ),
    schema="AP242",
)


def _render_m124() -> str:
    """Render AP209 file with FEA_MODEL_3D element referencing node outside node-set.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100-#103  CARTESIAN_POINTs (n1, n2, n3 in node-set; n4 outside)
      #110-#113  NODE entities (n1, n2, n3 in group; n4 exists but not in group)
      #200       VOLUME_3D_ELEMENT_DESCRIPTOR referencing (n1,n2,n3,n4) — DEFECT: n4 outside node-set
      #300       NODE_GROUP containing only (n1, n2, n3) — n4 excluded
      #310       FEA_MODEL_3D with its_node_set=#300, its_element_set containing #200
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M124: AP209 fea_model includes element referencing a node outside its node-set */")
    lines.append("/* DEFECT: FEA_MODEL_3D its_node_set = (n1,n2,n3); element references n4 which is outside */")
    lines.append("/* Node n4 exists in the file but is NOT a member of the model's NODE_GROUP */")
    lines.append("/* Per AP209 §6 all element nodes must be members of fea_model.its_node_set */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'FEA_MODEL_3D') */")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M124: AP209 FEA_MODEL_3D element references node outside node-set'),'2;1');")
    lines.append("FILE_NAME('M124.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('fea','3D'));")
    lines.append("/* Three nodes in the declared node-set */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(10.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(5.0,10.0,0.0));")
    lines.append("/* n4 is OUTSIDE the node-set — its CARTESIAN_POINT and NODE exist but are excluded */")
    lines.append("#103=CARTESIAN_POINT('n4',(5.0,5.0,10.0));")
    lines.append("#110=NODE('tet_n1',(#100),$);")
    lines.append("#111=NODE('tet_n2',(#101),$);")
    lines.append("#112=NODE('tet_n3',(#102),$);")
    lines.append("/* #113 = n4: present in file but NOT in NODE_GROUP #300 — the node-set leak */")
    lines.append("#113=NODE('tet_n4_outside',(#103),$);")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* DEFECT: element references #113 (n4) which is outside the model node-set #300 */")
    lines.append("/* A valid element would only reference nodes that are members of its_node_set */")
    lines.append("#200=VOLUME_3D_ELEMENT_DESCRIPTOR('leak_tet','linear_tetrahedron',")
    lines.append("  (#110,#111,#112,#113));")
    lines.append("/* NODE_GROUP: only the 3 declared nodes; n4 (#113) is intentionally omitted */")
    lines.append("#300=NODE_GROUP('declared_nodes',(#110,#111,#112),$);")
    lines.append("/* Byte assertion: contains(b'FEA_MODEL_3D') */")
    lines.append("/* DEFECT: its_element_set contains #200 whose 4th node (#113) is outside its_node_set #300 */")
    lines.append("#310=FEA_MODEL_3D('node_set_leak_model',$,'',(#300),(#200),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-fea-model-element-outside-node-set',")
    lines.append("  (#110,#111,#112,#113,#200,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M124','M124','M124',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m124(path) -> None:
    Path(path).write_text(_render_m124())


f.render = _render_m124  # type: ignore[method-assign]
f.write = _write_m124    # type: ignore[method-assign]
