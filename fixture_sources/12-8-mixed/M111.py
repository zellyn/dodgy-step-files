"""M111 — AP209 single_point_constraint applied to a node not in the mesh.

Catalog claim: A SINGLE_POINT_CONSTRAINT references a NODE by id, but
that node is not in any FEA_MODEL_3D's node set. The constraint applies to
no degree of freedom and the corresponding row/column never enters the
stiffness matrix; the model is effectively unconstrained at that
fictitious point.

Reproducer recipe: A NODE #999 not in any model's its_node_set,
referenced by SINGLE_POINT_CONSTRAINT(#999, ..).

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'SINGLE_POINT_CONSTRAINT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M111",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 SINGLE_POINT_CONSTRAINT referencing "
        "a NODE that is not included in any FEA_MODEL_3D node set; "
        "input: AP209 STEP file where NODE #999 is declared in the file but is NOT "
        "a member of any FEA_MODEL_3D its_node_set; a SINGLE_POINT_CONSTRAINT entity "
        "references node #999 to apply a fixed-displacement boundary condition; "
        "per ISO 10303-209 §7 fea_model node-set membership invariant, every "
        "boundary condition must reference a node that belongs to the model's active "
        "node set; when the target node is absent from the node set, the corresponding "
        "stiffness-matrix row and column are never assembled; the constraint applies to "
        "no degree of freedom, the model is effectively unconstrained at the "
        "fictitious attachment point, and a rigid-body mode exists in the solution; "
        "a solver will either detect the singularity and abort or silently proceed "
        "with a numerically ill-conditioned factorization; "
        "kernel must detect orphan-node constraints; warn and skip the constraint, "
        "or reject the file; "
        "synonyms: AP209 BC applied to nothing, FEM constraint on missing node, "
        "SPC dangling reference, AP209 SPC orphan node, "
        "boundary condition on missing node, FEM constraint references node not in mesh, "
        "single_point_constraint targets unknown node"
    ),
    schema="AP242",
)


def _render_m111() -> str:
    """Render AP209 file with SINGLE_POINT_CONSTRAINT referencing an orphan node.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#101 CARTESIAN_POINTs for model nodes (in the node set)
      #110-#111 NODE entities in the FEA model node set
      #200      CARTESIAN_POINT for the orphan node (NOT in node set)
      #999      NODE for the orphan (declared but NOT in model's node group)
      #300      NODE_GROUP containing only model nodes #110 and #111
      #310      FEA_MODEL referencing the node group (excludes #999)
      #400      SINGLE_POINT_CONSTRAINT applied to orphan node #999 — the defect
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M111: AP209 SINGLE_POINT_CONSTRAINT applied to node not in mesh */")
    lines.append("/* DEFECT: SINGLE_POINT_CONSTRAINT references #999 which is NOT in FEA_MODEL node set */")
    lines.append("/* Constraint applies to no DOF — stiffness matrix row/col never assembled */")
    lines.append("/* Model is effectively unconstrained — rigid-body mode exists */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M111: AP209 SPC on orphan node outside FEA model node set'),'2;1');")
    lines.append("FILE_NAME('M111.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#200=CARTESIAN_POINT('orphan',(50.0,0.0,50.0));")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') indirectly — node #999 */")
    lines.append("/* NODE #999 matches the id used in the catalog reproducer recipe */")
    lines.append("#999=NODE('orphan_bc_node',(#200),$);")
    lines.append("/* NODE_GROUP: model contains only #110 and #111 — NOT #999 */")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("#300=NODE_GROUP('model_nodes',(#110,#111),$);")
    lines.append("#310=FEA_MODEL('beam_model',$,'',(#300),(),());")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("/* DEFECT: SPC applied to #999 — orphan node outside the model node set *)  */")
    lines.append("/* Fixed-displacement BC: all 3 translations set to 0.0 (fixed wall) */")
    lines.append("/* The corresponding stiffness matrix row/column is never assembled *)  */")
    lines.append("/* Model has a free rigid-body mode at the supposed support point *)  */")
    lines.append("#400=SINGLE_POINT_CONSTRAINT('spc_fixed',#999,(.TRUE.,.TRUE.,.TRUE.),$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-spc-on-orphan-node-not-in-mesh',")
    lines.append("  (#110,#111,#999,#310,#400));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M111','M111','M111',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m111(path) -> None:
    Path(path).write_text(_render_m111())


f.render = _render_m111  # type: ignore[method-assign]
f.write = _write_m111    # type: ignore[method-assign]
