"""M148 — AP210 same NETWORK identifier used for two unrelated nets

Catalog claim: Two NETWORK entities both declare the name 'VCC' yet
route different conductors with no common node. A net-by-name lookup
returns one or the other depending on instance ordering. Connectivity
tools merge unrelated traces, breaking impedance / continuity checks.

Reproducer recipe: two NETWORK('VCC',..) entities each with a
distinct, non-overlapping NETWORK_NODE set.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  count_entity_def(b'NETWORK') >= 2
  contains(b"NETWORK('VCC',")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M148",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where two distinct NETWORK entities both declare the name 'VCC' but route "
        "different, non-overlapping conductors with no shared NETWORK_NODE; "
        "input: AP210 STEP file containing two NETWORK instances both named 'VCC': "
        "#200 NETWORK('VCC') groups #100 ('vcc_node_a1') and #101 ('vcc_node_a2') — "
        "the power rail on sub-design A; "
        "#201 NETWORK('VCC') groups #102 ('vcc_node_b1') and #103 ('vcc_node_b2') — "
        "the power rail on sub-design B; "
        "these two NETWORK entities have no common NETWORK_NODE and are electrically "
        "independent conductors representing different power distribution sub-circuits; "
        "a net-by-name lookup for 'VCC' returns either #200 or #201 depending on "
        "instance ordering in the file; connectivity tools merge both sets of traces "
        "under one net name, breaking impedance continuity and design-rule checks; "
        "per ISO 10303-210 §7 NETWORK.name must be unique within a design; "
        "kernel must validate NETWORK identifier uniqueness and reject or rename one "
        "with a diagnostic; "
        "synonyms: AP210 two nets named VCC, PCB net name collision, ECAD duplicate net name, "
        "PCB net name collision, AP210 duplicate net, ECAD net namespace conflict"
    ),
    schema="AP242",
)


def _render_m148() -> str:
    """Render AP210 file with two NETWORK entities both named 'VCC'.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      NETWORK_NODE 'vcc_node_a1' — sub-design A, rail segment 1
      #101      NETWORK_NODE 'vcc_node_a2' — sub-design A, rail segment 2
      #102      NETWORK_NODE 'vcc_node_b1' — sub-design B, rail segment 1
      #103      NETWORK_NODE 'vcc_node_b2' — sub-design B, rail segment 2
      #200      NETWORK('VCC') — sub-design A net  (DEFECT: duplicate name)
      #201      NETWORK('VCC') — sub-design B net  (DEFECT: duplicate name)
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M148: AP210 same NETWORK identifier used for two unrelated nets */")
    lines.append("/* DEFECT: two NETWORK entities both named 'VCC' route different conductors */")
    lines.append("/* Sub-design A VCC and sub-design B VCC are electrically independent */")
    lines.append("/* Net-by-name lookup returns either #200 or #201 — ordering-dependent */")
    lines.append("/* Connectivity tools merge unrelated traces, breaking continuity checks */")
    lines.append("/* Per ISO 10303-210 §7 NETWORK.name must be unique within a design */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'NETWORK') >= 2 */")
    lines.append("/* Byte assertion: contains(b\"NETWORK('VCC',\") */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M148: AP210 duplicate NETWORK name VCC'),'2;1');")
    lines.append("FILE_NAME('M148.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Sub-design A power rail nodes — independent conductor set */")
    lines.append("#100=NETWORK_NODE('vcc_node_a1',());")
    lines.append("#101=NETWORK_NODE('vcc_node_a2',());")
    lines.append("/* Sub-design B power rail nodes — different independent conductor set */")
    lines.append("#102=NETWORK_NODE('vcc_node_b1',());")
    lines.append("#103=NETWORK_NODE('vcc_node_b2',());")
    lines.append("/* Byte assertion: count_entity_def(b'NETWORK') >= 2 */")
    lines.append("/* Byte assertion: contains(b\"NETWORK('VCC',\") */")
    lines.append("/* DEFECT: both networks named 'VCC' but route different conductors */")
    lines.append("/* Sub-design A VCC net — routes vcc_node_a1 and vcc_node_a2 */")
    lines.append("#200=NETWORK('VCC',(#100,#101));")
    lines.append("/* Sub-design B VCC net — routes vcc_node_b1 and vcc_node_b2 */")
    lines.append("/* No shared nodes with #200 — these are unrelated conductors */")
    lines.append("#201=NETWORK('VCC',(#102,#103));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-duplicate-network-name-vcc-two-unrelated-nets',")
    lines.append("  (#100,#101,#102,#103,#200,#201));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M148','M148','M148',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m148(path) -> None:
    Path(path).write_text(_render_m148())


f.render = _render_m148  # type: ignore[method-assign]
f.write = _write_m148    # type: ignore[method-assign]
