"""M115 — AP209 nodal force distribution with negative weights.

Catalog claim: A NODE_WITH_FORCE is part of a distributed load whose
per-node weights include negative values, e.g. weights (0.6, 0.6, -0.2)
summing to 1.0. The distribution forces a pulling contribution at the
third node when the resultant force is downward. While the resultant is
preserved, the local load shape is unphysical.

Reproducer recipe: Three NODE_WITH_FORCE entries with force distribution
factors 0.6, 0.6, -0.2.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'NODE_WITH_FORCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M115",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 NODE_WITH_FORCE entities where the distributed "
        "load weights include a negative value — distribution factors are (0.6, 0.6, -0.2); "
        "input: AP209 STEP file with three NODE_WITH_FORCE entities sharing a distributed "
        "load resultant; the per-node distribution factors are 0.6, 0.6, and -0.2, summing "
        "to 1.0; the sum is formally correct but the negative weight at the third node forces "
        "a pulling (tensile) contribution when the resultant force is downward (compressive); "
        "per ISO 10303-209 §7 nodal_load distribution_factor convention, all per-node weights "
        "must be non-negative and sum to 1.0; a negative weight is unphysical: it applies a "
        "force in the opposite direction to the resultant at that node, creating artificial "
        "stress concentrations; the local load shape does not match the user's intent; "
        "kernel must validate non-negative distribution factors; warn, normalize to "
        "non-negative, or reject as malformed; "
        "synonyms: negative load fraction, AP209 distribution wrong sign, load weights include "
        "negative, FEM distributed load pulls instead of pushes, AP209 negative load weight, "
        "FEM unphysical distribution, node pulled instead of pushed"
    ),
    schema="AP242",
)


def _render_m115() -> str:
    """Render AP209 file with NODE_WITH_FORCE distribution factors (0.6, 0.6, -0.2).

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#102 CARTESIAN_POINTs for three load nodes
      #110-#112 NODE entities
      #300      NODE_GROUP containing all three nodes
      #310      FEA_MODEL referencing the node group
      #400-#402 NODE_WITH_FORCE: distribution factors 0.6, 0.6, -0.2 — DEFECT
      #500      GEOMETRIC_CURVE_SET model entity
      #600+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M115: AP209 nodal force distribution with negative weight */")
    lines.append("/* DEFECT: NODE_WITH_FORCE distribution factors (0.6, 0.6, -0.2) */")
    lines.append("/* Negative weight at third node pulls instead of pushes — unphysical */")
    lines.append("/* Per AP209 §7, all distribution factors must be non-negative */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M115: AP209 distributed load with negative weight factor'),'2;1');")
    lines.append("FILE_NAME('M115.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Three nodes receiving the distributed load */")
    lines.append("#100=CARTESIAN_POINT('p1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('p2',(50.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('p3',(100.0,0.0,0.0));")
    lines.append("#110=NODE('load_node_1',(#100),$);")
    lines.append("#111=NODE('load_node_2',(#101),$);")
    lines.append("#112=NODE('load_node_3',(#102),$);")
    lines.append("/* NODE_GROUP: all three load nodes in the FEA model */")
    lines.append("#300=NODE_GROUP('load_nodes',(#110,#111,#112),$);")
    lines.append("#310=FEA_MODEL('load_model',$,'',(#300),(),());")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') */")
    lines.append("/* DEFECT: distribution factors 0.6 + 0.6 + (-0.2) = 1.0 but -0.2 is negative */")
    lines.append("/* Node 1: factor 0.6 — downward force component (F_z = -1000.0 * 0.6 = -600 N) */")
    lines.append("#400=NODE_WITH_FORCE('nwf_1',#110,(0.0,0.0,-600.0),$,0.6);")
    lines.append("/* Node 2: factor 0.6 — downward force component (F_z = -1000.0 * 0.6 = -600 N) */")
    lines.append("#401=NODE_WITH_FORCE('nwf_2',#111,(0.0,0.0,-600.0),$,0.6);")
    lines.append("/* Node 3: factor -0.2 — DEFECT: negative weight pulls upward against resultant */")
    lines.append("/* F_z = -1000.0 * (-0.2) = +200 N (upward) when resultant is downward */")
    lines.append("/* This is unphysical; stress concentrations appear at this node *)  */")
    lines.append("#402=NODE_WITH_FORCE('nwf_3',#112,(0.0,0.0,200.0),$,-0.2);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-nodal-force-distribution-negative-weights',")
    lines.append("  (#110,#111,#112,#310,#400,#401,#402));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M115','M115','M115',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m115(path) -> None:
    Path(path).write_text(_render_m115())


f.render = _render_m115  # type: ignore[method-assign]
f.write = _write_m115    # type: ignore[method-assign]
