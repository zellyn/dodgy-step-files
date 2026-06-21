"""M155 — AP210 net connectivity ends at a non-pin element

Catalog claim: A NETWORK_NODE references a CARTESIAN_POINT instead of
a TERMINAL. The trace ends in the middle of nothing — there is no
electrical pin at the endpoint. The net topology is broken.

Reproducer recipe: NETWORK_NODE('node_floating', cartesian_point)
in a NETWORK list.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'NETWORK_NODE')
  contains(b'CARTESIAN_POINT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M155",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a NETWORK_NODE references a CARTESIAN_POINT instead of a TERMINAL; "
        "input: AP210 STEP file containing a NETWORK 'PCB_NET' whose topology node "
        "NETWORK_NODE('node_floating') cites a CARTESIAN_POINT as its endpoint element; "
        "per ISO 10303-210 §7 a NETWORK_NODE must reference a TERMINAL (or compatible "
        "electrical endpoint subtype); a CARTESIAN_POINT is not a valid electrical endpoint; "
        "the trace ends in mid-air — the PCB routing graph has no pin at the endpoint; "
        "netlist continuity is broken; the ECAD exporter converted a routing-graph node "
        "from a point object without promoting it to a TERMINAL entity; "
        "kernel must validate NETWORK_NODE references point at TERMINAL and reject or warn; "
        "synonyms: AP210 net to non-pin, PCB trace ends at point, ECAD connectivity to "
        "non-terminal, AP210 endpoint not a pin, PCB trace dangling, ECAD net to wrong type"
    ),
    schema="AP242",
)


def _render_m155() -> str:
    """Render AP210 file with NETWORK_NODE referencing CARTESIAN_POINT not TERMINAL.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       CARTESIAN_POINT at (10.0, 5.0, 0.0) — wrongly used as NETWORK_NODE endpoint
      #51       TERMINAL 'T_start' — valid electrical start pin
      #52       CARTESIAN_POINT for T_start location
      #60       NETWORK_NODE 'node_start' referencing TERMINAL #51 (valid)
      #61       NETWORK_NODE 'node_floating' referencing CARTESIAN_POINT #50 (DEFECT)
      #70       NETWORK 'PCB_NET' grouping both nodes
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M155: AP210 net connectivity ends at a non-pin element */")
    lines.append("/* DEFECT: NETWORK_NODE 'node_floating' references CARTESIAN_POINT not TERMINAL */")
    lines.append("/* The PCB trace endpoint has no electrical pin — connectivity broken */")
    lines.append("/* ECAD exporter promoted a routing-graph point to a node without making a TERMINAL */")
    lines.append("/* Per ISO 10303-210 §7 NETWORK_NODE must reference a TERMINAL subtype */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NETWORK_NODE') */")
    lines.append("/* Byte assertion: contains(b'CARTESIAN_POINT') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M155: AP210 NETWORK_NODE references CARTESIAN_POINT not TERMINAL'),'2;1');")
    lines.append("FILE_NAME('M155.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* DEFECT: #50 is a CARTESIAN_POINT; a NETWORK_NODE will reference it below */")
    lines.append("/* A valid endpoint would be a TERMINAL, not a bare geometry point */")
    lines.append("#50=CARTESIAN_POINT('floating_endpoint',(10.0,5.0,0.0));")
    lines.append("/* Valid TERMINAL at the start of the trace */")
    lines.append("#52=CARTESIAN_POINT('T_start_loc',(0.0,5.0,0.0));")
    lines.append("#51=TERMINAL('T_start',#52);")
    lines.append("/* Byte assertion: contains(b'NETWORK_NODE') */")
    lines.append("/* NETWORK_NODE 'node_start' — valid: references a TERMINAL */")
    lines.append("#60=NETWORK_NODE('node_start',#51);")
    lines.append("/* DEFECT: NETWORK_NODE 'node_floating' references CARTESIAN_POINT #50 not TERMINAL */")
    lines.append("/* This trace end has no electrical pin; per AP210 this must be a TERMINAL */")
    lines.append("#61=NETWORK_NODE('node_floating',#50);")
    lines.append("/* NETWORK 'PCB_NET' groups both nodes — one valid, one defective */")
    lines.append("#70=NETWORK('PCB_NET',(#60,#61));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-net-endpoint-not-terminal-network-node-cartesian-point',")
    lines.append("  (#50,#51,#52,#60,#61,#70));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M155','M155','M155',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m155(path) -> None:
    Path(path).write_text(_render_m155())


f.render = _render_m155  # type: ignore[method-assign]
f.write = _write_m155    # type: ignore[method-assign]
