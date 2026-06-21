"""M078 — AP209 quadratic_hexahedron with wrong node count (12 instead of 20).

Catalog claim: A VOLUME_3D_ELEMENT_DESCRIPTOR declares quadratic_hexahedron
topology — which mandates 20 nodes (8 corner + 12 mid-edge) — but the
descriptor's node list contains only 12. The resulting element cannot be
evaluated as a quadratic hex; consumers either fall back to linear
interpolation silently or drop the element.

Reproducer recipe: VOLUME_3D_ELEMENT_DESCRIPTOR('quad_hex',
'quadratic_hexahedron', (n1..n12)) — 12 nodes for a topology requiring 20.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'quadratic_hexahedron')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M078",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 FEM element with wrong node count; "
        "input: AP209 STEP file where a VOLUME_3D_ELEMENT_DESCRIPTOR declares "
        "quadratic_hexahedron topology (which requires 20 nodes: 8 corner + 12 mid-edge) "
        "but the associated node list has only 12 entries; "
        "per ISO 10303-104 AP209 a quadratic hexahedron (C3D20) must have 20 nodes; "
        "with only 12 nodes the element is under-noded and cannot be integrated correctly "
        "as a serendipity element; consumers must drop the element with a warning or reject; "
        "kernel must validate node-count against the declared topology type and not "
        "silently fall back to linear interpolation with 8 corner nodes; "
        "synonyms: AP209 hex node count wrong, quadratic hex with 12 nodes not 20, "
        "FEA element node count wrong for hex8, AP209 element under-noded, "
        "hex element missing mid-edge nodes"
    ),
    schema="AP242",
)


def _render_m078() -> str:
    """Render AP209 file with quadratic_hexahedron declared with 12 nodes instead of 20.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#16   Unit context
      #100-#111 CARTESIAN_POINTs for 12 nodes (8 corners + 4 of 12 required mid-edge)
      #120-#131 NODE entities
      #200      VOLUME_3D_ELEMENT_DESCRIPTOR with quadratic_hexahedron, 12 nodes — defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M078: AP209 quadratic_hexahedron with wrong node count (12 instead of 20) */")
    lines.append("/* DEFECT: quadratic hex (C3D20) requires 20 nodes; only 12 provided */")
    lines.append("/* Element cannot be evaluated; consumers must drop or reject */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'quadratic_hexahedron') */")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M078: AP209 quadratic_hexahedron with 12 nodes not 20'),'2;1');")
    lines.append("FILE_NAME('M078.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* 8 corner nodes of unit cube */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(1.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(1.0,1.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(0.0,1.0,0.0));")
    lines.append("#104=CARTESIAN_POINT('n5',(0.0,0.0,1.0));")
    lines.append("#105=CARTESIAN_POINT('n6',(1.0,0.0,1.0));")
    lines.append("#106=CARTESIAN_POINT('n7',(1.0,1.0,1.0));")
    lines.append("#107=CARTESIAN_POINT('n8',(0.0,1.0,1.0));")
    lines.append("/* 4 mid-edge nodes (only 4 of 12 required; should be 12 mid-edge for C3D20) */")
    lines.append("#108=CARTESIAN_POINT('m1',(0.5,0.0,0.0));")
    lines.append("#109=CARTESIAN_POINT('m2',(1.0,0.5,0.0));")
    lines.append("#110=CARTESIAN_POINT('m3',(0.5,1.0,0.0));")
    lines.append("#111=CARTESIAN_POINT('m4',(0.0,0.5,0.0));")
    lines.append("/* NODE entities for the 12 geometry points */")
    lines.append("#120=NODE('n1',(#100),$);")
    lines.append("#121=NODE('n2',(#101),$);")
    lines.append("#122=NODE('n3',(#102),$);")
    lines.append("#123=NODE('n4',(#103),$);")
    lines.append("#124=NODE('n5',(#104),$);")
    lines.append("#125=NODE('n6',(#105),$);")
    lines.append("#126=NODE('n7',(#106),$);")
    lines.append("#127=NODE('n8',(#107),$);")
    lines.append("#128=NODE('m1',(#108),$);")
    lines.append("#129=NODE('m2',(#109),$);")
    lines.append("#130=NODE('m3',(#110),$);")
    lines.append("#131=NODE('m4',(#111),$);")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* Byte assertion: contains(b'quadratic_hexahedron') */")
    lines.append("/* DEFECT: quadratic_hexahedron requires 20 nodes; only 12 listed */")
    lines.append("#200=VOLUME_3D_ELEMENT_DESCRIPTOR('quad_hex','quadratic_hexahedron',")
    lines.append("  (#120,#121,#122,#123,#124,#125,#126,#127,#128,#129,#130,#131));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-quadratic-hexahedron-12-nodes-not-20',")
    lines.append("  (#120,#121,#122,#123,#124,#125,#126,#127,#128,#129,#130,#131,#200));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M078','M078','M078',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m078(path) -> None:
    Path(path).write_text(_render_m078())


f.render = _render_m078  # type: ignore[method-assign]
f.write = _write_m078    # type: ignore[method-assign]
