"""M144 — AP210 NETWORK_NODE chain forms a cycle (signal feedback path)

Catalog claim: NETWORK_NODE entries link node A -> B -> C -> A.
A connectivity walk of the net never terminates. The net is
electrically nonsensical for a non-feedback signal: a clock
distribution net is short-circuited to itself.

Reproducer recipe: three NETWORK_NODEs and a NETWORK listing
them in cyclic order without a DAG terminating step.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  count_entity_def(b'NETWORK_NODE') >= 3
  contains(b'NETWORK')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M144",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where NETWORK_NODE entries form a cycle: node_A references node_B, node_B "
        "references node_C, and node_C references back to node_A; "
        "input: AP210 STEP file containing three NETWORK_NODE instances — #100 ('node_A'), "
        "#101 ('node_B'), #102 ('node_C') — where each node's next-node attribute points "
        "to the following node in the ring; a NETWORK 'CLK_NET' groups all three nodes; "
        "a connectivity walk of CLK_NET starting at node_A visits node_B, then node_C, "
        "then returns to node_A and never terminates; "
        "the net is electrically nonsensical for a non-feedback signal: a clock "
        "distribution net is short-circuited to itself; "
        "per ISO 10303-210 §7 network connectivity must form a DAG (directed acyclic graph) "
        "for non-feedback signals; "
        "kernel must detect cycles in the net connectivity graph and reject or warn; "
        "synonyms: AP210 net cycle, PCB net loop, ECAD signal feedback path, "
        "AP210 connectivity cycle, PCB signal connectivity cycle, ECAD net never terminates"
    ),
    schema="AP242",
)


def _render_m144() -> str:
    """Render AP210 file with three NETWORK_NODEs forming a cycle A->B->C->A.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      NETWORK_NODE 'node_A' — next: node_B
      #101      NETWORK_NODE 'node_B' — next: node_C
      #102      NETWORK_NODE 'node_C' — next: node_A  (cycle closes here)
      #110      NETWORK 'CLK_NET' grouping all three nodes
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M144: AP210 NETWORK_NODE chain forms a cycle (signal feedback path) */")
    lines.append("/* DEFECT: node_A -> node_B -> node_C -> node_A — cycle never terminates */")
    lines.append("/* Non-feedback clock net CLK_NET is electrically short-circuited to itself */")
    lines.append("/* Per ISO 10303-210 §7 net connectivity must be acyclic for non-feedback signals */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'NETWORK_NODE') >= 3 */")
    lines.append("/* Byte assertion: contains(b'NETWORK') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M144: AP210 NETWORK_NODE cyclic connectivity'),'2;1');")
    lines.append("FILE_NAME('M144.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* Byte assertion: count_entity_def(b'NETWORK_NODE') >= 3 */")
    lines.append("/* Three NETWORK_NODEs forming a cycle: A -> B -> C -> A */")
    lines.append("/* node_A connects to node_B */")
    lines.append("#100=NETWORK_NODE('node_A',(#101));")
    lines.append("/* node_B connects to node_C */")
    lines.append("#101=NETWORK_NODE('node_B',(#102));")
    lines.append("/* DEFECT: node_C connects back to node_A — closes the cycle */")
    lines.append("#102=NETWORK_NODE('node_C',(#100));")
    lines.append("/* Byte assertion: contains(b'NETWORK') */")
    lines.append("/* CLK_NET groups all three cyclic nodes — walk never terminates */")
    lines.append("#110=NETWORK('CLK_NET',(#100,#101,#102));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-network-node-cycle-signal-feedback-path',")
    lines.append("  (#100,#101,#102,#110));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M144','M144','M144',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m144(path) -> None:
    Path(path).write_text(_render_m144())


f.render = _render_m144  # type: ignore[method-assign]
f.write = _write_m144    # type: ignore[method-assign]
