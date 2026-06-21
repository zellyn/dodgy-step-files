"""M112 — AP209 multi_point_constraint chain forms a dependency cycle.

Catalog claim: Three MULTI_POINT_CONSTRAINT entries form a cycle:
node A is a slave of node B (constraint X), node B is a slave of node C
(constraint Y), node C is a slave of node A (constraint Z). Solver
assembly cannot resolve the master-slave reduction; either the matrix is
singular or the system iterates indefinitely.

Reproducer recipe: Three MULTI_POINT_CONSTRAINT entities forming A→B→C→A.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  count_entity_def(b'MULTI_POINT_CONSTRAINT') >= 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M112",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 MULTI_POINT_CONSTRAINT entities forming "
        "a cyclic master-slave dependency A→B→C→A; "
        "input: AP209 STEP file where three MULTI_POINT_CONSTRAINT entities each designate "
        "one node as slave and another as master, forming a directed cycle: node_A is slave "
        "to node_B in constraint_X, node_B is slave to node_C in constraint_Y, node_C is "
        "slave to node_A in constraint_Z; "
        "per ISO 10303-209 §7 multi_point_constraint master/slave acyclic-graph requirement, "
        "the constraint dependency graph must be a directed acyclic graph (DAG); "
        "a cycle in the MPC graph means the slave reduction cannot be resolved: the "
        "assembled stiffness matrix is either singular (row/column elimination loops) "
        "or the iterative solver diverges; the FEA result is undefined; "
        "kernel must detect cycle in MPC graph and reject as malformed, reporting which "
        "nodes participate in the cycle; "
        "synonyms: MPC loop, AP209 master-slave cycle, multi_point_constraint dependency cycle, "
        "MPC dependency cycle, FEM constraint chain loops, AP209 MPC cycle, "
        "FEM constraint chain has loop, master-slave loop in STEP file"
    ),
    schema="AP242",
)


def _render_m112() -> str:
    """Render AP209 file with three MULTI_POINT_CONSTRAINT entities forming A→B→C→A cycle.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#102 CARTESIAN_POINTs for three nodes
      #110-#112 NODE entities (A, B, C)
      #300      NODE_GROUP containing all three nodes
      #310      FEA_MODEL referencing the node group
      #400      MULTI_POINT_CONSTRAINT: A (slave) → B (master) — first link
      #401      MULTI_POINT_CONSTRAINT: B (slave) → C (master) — second link
      #402      MULTI_POINT_CONSTRAINT: C (slave) → A (master) — CYCLE closes here
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M112: AP209 MULTI_POINT_CONSTRAINT chain forms a dependency cycle */")
    lines.append("/* DEFECT: A→B→C→A MPC cycle — solver cannot resolve master-slave reduction */")
    lines.append("/* Stiffness matrix singular; FEA result undefined; must be rejected */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'MULTI_POINT_CONSTRAINT') >= 3 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M112: AP209 MPC dependency cycle A->B->C->A'),'2;1');")
    lines.append("FILE_NAME('M112.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Three nodes forming the MPC cycle */")
    lines.append("#100=CARTESIAN_POINT('node_A',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('node_B',(100.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('node_C',(50.0,100.0,0.0));")
    lines.append("#110=NODE('node_A',(#100),$);")
    lines.append("#111=NODE('node_B',(#101),$);")
    lines.append("#112=NODE('node_C',(#102),$);")
    lines.append("/* NODE_GROUP: all three nodes in the FEA model */")
    lines.append("#300=NODE_GROUP('all_nodes',(#110,#111,#112),$);")
    lines.append("#310=FEA_MODEL('triangle_model',$,'',(#300),(),());")
    lines.append("/* DEFECT: three MPCs forming A→B→C→A directed cycle */")
    lines.append("/* Byte assertion: count_entity_def(b'MULTI_POINT_CONSTRAINT') >= 3 */")
    lines.append("/* Constraint X: node_A is slave, node_B is master */")
    lines.append("#400=MULTI_POINT_CONSTRAINT('mpc_AB',#110,(#111),$);")
    lines.append("/* Constraint Y: node_B is slave, node_C is master */")
    lines.append("#401=MULTI_POINT_CONSTRAINT('mpc_BC',#111,(#112),$);")
    lines.append("/* Constraint Z: node_C is slave, node_A is master — CYCLE CLOSES HERE */")
    lines.append("/* ISO 10303-209 §7 requires acyclic DAG; this violates the invariant */")
    lines.append("#402=MULTI_POINT_CONSTRAINT('mpc_CA',#112,(#110),$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-multi-point-constraint-dependency-cycle',")
    lines.append("  (#110,#111,#112,#310,#400,#401,#402));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M112','M112','M112',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m112(path) -> None:
    Path(path).write_text(_render_m112())


f.render = _render_m112  # type: ignore[method-assign]
f.write = _write_m112    # type: ignore[method-assign]
