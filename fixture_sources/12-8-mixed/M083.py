"""M083 — AP209 nodal load applied to a node not in the model node set.

Catalog claim: A NODE_WITH_FORCE references a NODE by id, but that node
is not part of any FEA_MODEL_3D's its_node_set. The load floats free of
the discretized model and contributes nothing to the assembled load vector.

Reproducer recipe: FEA_MODEL whose its_node_set excludes #210, combined
with NODE_WITH_FORCE(#210, ..).

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'NODE_WITH_FORCE')
  contains(b'FEA_MODEL')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M083",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 nodal load applied to a node outside "
        "the active FEA model node set; "
        "input: AP209 STEP file where NODE_WITH_FORCE references orphan node #210 but "
        "NODE_GROUP 'model_nodes' contains only nodes #110 and #111, and FEA_MODEL "
        "references that node group — node #210 is declared in the file as a NODE "
        "but is excluded from the model's node set; "
        "per ISO 10303-209 §7 fea_model node-set invariants every force/load entity must "
        "reference a node that belongs to the model's node set; "
        "when the target node is outside the node set the load floats free, contributes "
        "zero to the assembled load vector, and is silently ignored by any solver reading "
        "the file; "
        "kernel must warn on loads attached to nodes outside the active model node set; "
        "either heal (snap to nearest model node) or drop it with a warning; "
        "synonyms: orphan node load, FEM load not applied, AP209 force on orphan node, "
        "load went to nothing, AP209 force on phantom node, load applied to node not in model, "
        "nodal load floats free"
    ),
    schema="AP242",
)


def _render_m083() -> str:
    """Render AP209 file with NODE_WITH_FORCE referencing a node outside FEA_MODEL node set.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#101 CARTESIAN_POINTs for model nodes (in the node set)
      #110-#111 NODE entities in the FEA model node set
      #200      CARTESIAN_POINT for the orphan node (NOT in node set)
      #210      NODE for the orphan (declared but NOT in model's node group)
      #300      NODE_GROUP containing only model nodes #110 and #111
      #310      FEA_MODEL referencing the node group (excludes #210)
      #400      NODE_WITH_FORCE applied to orphan node #210 — the defect
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M083: AP209 nodal load applied to a node not in the model node set */")
    lines.append("/* DEFECT: NODE_WITH_FORCE references #210 which is NOT in FEA_MODEL node set */")
    lines.append("/* Load floats free — contributes nothing to assembled load vector */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') */")
    lines.append("/* Byte assertion: contains(b'FEA_MODEL') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M083: AP209 nodal load on node outside FEA model node set'),'2;1');")
    lines.append("FILE_NAME('M083.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Model nodes: two nodes that ARE in the FEA model node set */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(100.0,0.0,0.0));")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("#111=NODE('n2',(#101),$);")
    lines.append("/* Orphan node: declared in file but excluded from model node group */")
    lines.append("#200=CARTESIAN_POINT('orphan',(50.0,50.0,0.0));")
    lines.append("#210=NODE('orphan_node',(#200),$);")
    lines.append("/* NODE_GROUP: model contains only #110 and #111 — NOT #210 */")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') indirectly via next entity */")
    lines.append("/* Byte assertion: contains(b'FEA_MODEL') */")
    lines.append("#300=NODE_GROUP('model_nodes',(#110,#111),$);")
    lines.append("#310=FEA_MODEL('beam_model',$,'',(#300),(),());")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') */")
    lines.append("/* DEFECT: NODE_WITH_FORCE applied to #210 — orphan node outside model node set */")
    lines.append("/* Force of 1000 N in X direction applied to a phantom node */")
    lines.append("/* The load contributes nothing to the assembled load vector */")
    lines.append("#400=NODE_WITH_FORCE(#210,((1000.0,0.0,0.0)),'pull_x');")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-nodal-load-on-orphan-node-outside-model',")
    lines.append("  (#110,#111,#210,#310,#400));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M083','M083','M083',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m083(path) -> None:
    Path(path).write_text(_render_m083())


f.render = _render_m083  # type: ignore[method-assign]
f.write = _write_m083    # type: ignore[method-assign]
