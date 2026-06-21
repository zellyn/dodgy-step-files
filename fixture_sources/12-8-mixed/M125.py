"""M125 — AP209 node_group declares the same node id twice.

Catalog claim: A NODE_GROUP contains the same NODE reference twice (e.g.
(#100, #101, #100)). Constraints / loads applied to the group act twice on
the duplicated node; the load is doubled or the BC is over-constrained.

Reproducer recipe: NODE_GROUP('fixed', (#100, #101, #100), $).

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'NODE_GROUP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M125",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 NODE_GROUP with a duplicate node "
        "reference (#100 appears at positions 1 and 3 in the group list); "
        "input: AP209 STEP file where a NODE_GROUP entity lists its members as "
        "( #100, #101, #100 ) — node #100 appears twice; per ISO 10303-209 §7 "
        "node_group set-semantics, a NODE_GROUP is a set and must not repeat the "
        "same NODE reference; when a boundary condition or load is applied to this "
        "group the duplicated node receives a doubled constraint contribution: "
        "a fixed-DOF BC applied twice over-constrains the node (redundant equation "
        "in the solver) and a force load applied twice doubles the applied load on "
        "that node while leaving all others correct; the analysis result is "
        "non-physical because the load vector or stiffness matrix is assembled "
        "incorrectly at the duplicated DOF; "
        "kernel must deduplicate silently and warn, or reject as malformed; "
        "synonyms: AP209 duplicate node in group, node-set with repeats, "
        "node group lists same id twice, duplicate NODE in NODE_GROUP, "
        "FEM load applied 2x to one node, AP209 node group has duplicate, "
        "node-group set semantics violated"
    ),
    schema="AP242",
)


def _render_m125() -> str:
    """Render AP209 file with NODE_GROUP containing a duplicate node reference.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100-#101  CARTESIAN_POINTs (two distinct node positions)
      #110-#111  NODE entities (n1, n2)
      #200       SINGLE_POINT_CONSTRAINT applied to the group
      #300       NODE_GROUP('fixed', (#110, #111, #110), $) — DEFECT: #110 listed twice
      #310       FEA_MODEL
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M125: AP209 node_group declares the same node id twice */")
    lines.append("/* DEFECT: NODE_GROUP member list = (#110, #111, #110) — node #110 appears twice */")
    lines.append("/* Per AP209 §7 node_group uses set semantics; duplicates violate the invariant */")
    lines.append("/* Load/BC applied to group acts twice on #110: load doubled or BC over-constrained */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NODE_GROUP') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M125: AP209 NODE_GROUP with duplicate node reference'),'2;1');")
    lines.append("FILE_NAME('M125.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Two distinct node positions */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(10.0,0.0,0.0));")
    lines.append("#110=NODE('fixed_n1',(#100),$);")
    lines.append("#111=NODE('fixed_n2',(#101),$);")
    lines.append("/* AXIS2_PLACEMENT_3D for the constraint orientation */")
    lines.append("#120=DIRECTION('z_dir',(0.0,0.0,1.0));")
    lines.append("#121=AXIS2_PLACEMENT_3D('bc_frame',#100,#120,$);")
    lines.append("#200=SINGLE_POINT_CONSTRAINT('fixed_bc','fixed',")
    lines.append("  #110,#121,(1,2,3),(0.0,0.0,0.0,$,$,$));")
    lines.append("/* Byte assertion: contains(b'NODE_GROUP') */")
    lines.append("/* DEFECT: member list is (#110, #111, #110) — #110 listed at positions 1 and 3 */")
    lines.append("/* A valid set-semantics group would be (#110, #111) with each node unique */")
    lines.append("#300=NODE_GROUP('fixed',(#110,#111,#110),$);")
    lines.append("#310=FEA_MODEL('duplicate_node_group_model',$,'',(#300),(),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-node-group-duplicate-node-reference',")
    lines.append("  (#110,#111,#200,#300,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M125','M125','M125',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m125(path) -> None:
    Path(path).write_text(_render_m125())


f.render = _render_m125  # type: ignore[method-assign]
f.write = _write_m125    # type: ignore[method-assign]
