"""M079 — AP209 boundary condition with no nodes attached.

Catalog claim: A SINGLE_POINT_CONSTRAINT is declared with a freedoms list
and a non-zero b value, but the NODE_GROUP it points at is empty (or the
constrained_node attribute is unresolved). The constraint applies to no
degrees of freedom.

Reproducer recipe: NODE_GROUP('fixed_nodes', (), $) (empty) referenced
by SINGLE_POINT_CONSTRAINT(..).

Byte assertions:
  contains(b'SINGLE_POINT_CONSTRAINT')
  contains(b'NODE_GROUP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M079",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 boundary condition with no nodes attached; "
        "input: AP209 STEP file where a SINGLE_POINT_CONSTRAINT references a "
        "FREEDOM_AND_COEFFICIENT with non-zero b value and the NODE_GROUP it points at "
        "is empty — NODE_GROUP('fixed_nodes', (), $) with an empty node list; "
        "the constraint has no nodes to apply to: it constrains zero degrees of freedom; "
        "per AP209 §7 constraint association rules every SINGLE_POINT_CONSTRAINT must "
        "have at least one node in its associated node group; "
        "an empty NODE_GROUP means the BC silently applies to nothing; "
        "kernel must detect unattached constraints, warn and skip or reject as malformed; "
        "kernel must never silently apply to all nodes or silently ignore the constraint; "
        "synonyms: AP209 boundary condition has no nodes, FEM constraint applies to nothing, "
        "empty NODE_GROUP on constraint, BC node-set unresolved, "
        "AP209 boundary condition empty"
    ),
    schema="AP242",
)


def _render_m079() -> str:
    """Render AP209 file with SINGLE_POINT_CONSTRAINT referencing empty NODE_GROUP.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context
      #100      CARTESIAN_POINT for a node (declared but not in the group)
      #110      NODE referencing the point
      #120      FREEDOMS_LIST (.X., .Y., .Z.)
      #130      FREEDOM_AND_COEFFICIENT referencing freedoms
      #140      NODE_GROUP('fixed_nodes', (), $) — empty, the defect
      #200      SINGLE_POINT_CONSTRAINT referencing the empty node group
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M079: AP209 boundary condition with no nodes attached */")
    lines.append("/* DEFECT: NODE_GROUP('fixed_nodes', (), $) is empty — constraint applies to nothing */")
    lines.append("/* SINGLE_POINT_CONSTRAINT references empty node group */")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("/* Byte assertion: contains(b'NODE_GROUP') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M079: AP209 boundary condition with no nodes attached'),'2;1');")
    lines.append("FILE_NAME('M079.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* A valid node — declared but not included in the (empty) node group */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("/* Constraint freedoms: X, Y, Z */")
    lines.append("#120=FREEDOMS_LIST((.X.,.Y.,.Z.));")
    lines.append("#130=FREEDOM_AND_COEFFICIENT(#120,1.0);")
    lines.append("/* Byte assertion: contains(b'NODE_GROUP') */")
    lines.append("/* DEFECT: NODE_GROUP with empty node list — constraint has nowhere to apply */")
    lines.append("#140=NODE_GROUP('fixed_nodes',(),$);")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("/* SINGLE_POINT_CONSTRAINT referencing the empty node group */")
    lines.append("/* b=0.0 (prescribed value); effectively applies to zero nodes */")
    lines.append("#200=SINGLE_POINT_CONSTRAINT($,#130,0.0,#140);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-boundary-condition-empty-node-group',")
    lines.append("  (#110,#130,#140,#200));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M079','M079','M079',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m079(path) -> None:
    Path(path).write_text(_render_m079())


f.render = _render_m079  # type: ignore[method-assign]
f.write = _write_m079    # type: ignore[method-assign]
