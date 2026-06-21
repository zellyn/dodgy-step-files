"""M109 — AP209 linear_hexahedron with only 4 nodes (should be 8).

Catalog claim: A VOLUME_3D_ELEMENT_DESCRIPTOR declares linear_hexahedron
topology — which mandates 8 corner nodes — but lists only 4 nodes in its
node-reference list. The descriptor cannot be evaluated as a hex; consumers
may treat as a degenerate tet, drop the element silently, or reject the file.

Reproducer recipe: VOLUME_3D_ELEMENT_DESCRIPTOR('lin_hex',
'linear_hexahedron', (n1,n2,n3,n4)) — 4 nodes for a topology requiring 8.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'linear_hexahedron')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M109",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 FEM volume element with wrong node count; "
        "input: AP209 STEP file where a VOLUME_3D_ELEMENT_DESCRIPTOR declares "
        "linear_hexahedron topology (which requires exactly 8 corner nodes for a C3D8 "
        "trilinear brick element) but the associated node list has only 4 entries; "
        "per ISO 10303-104 AP209 fea topology rules §6, a linear hexahedron must have "
        "8 corner nodes forming 6 quadrilateral faces with trilinear isoparametric "
        "interpolation; providing only 4 nodes means the element degenerates to a "
        "shape with 4 undefined corners; consumers may treat the 4-node set as a "
        "tetrahedron (linear tet), silently drop the hex element, or reject the file; "
        "in no case can the element be integrated correctly as a C3D8 brick; "
        "kernel must validate node-count against declared topology; "
        "drop the element with a warning or reject; "
        "synonyms: AP209 hex element has 4 nodes, linear hex with too few nodes, "
        "FEM element reduces to tet, AP209 hex with 4 nodes, "
        "linear_hexahedron node count too low, FEA element node count wrong for hex8, "
        "hex element missing 4 corner nodes, hex degenerated to tet shape"
    ),
    schema="AP242",
)


def _render_m109() -> str:
    """Render AP209 file with linear_hexahedron declared with only 4 nodes instead of 8.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#103 CARTESIAN_POINTs for 4 nodes (corner subset of a unit cube — missing 4)
      #110-#113 NODE entities for the 4 nodes
      #200      VOLUME_3D_ELEMENT_DESCRIPTOR 'lin_hex' linear_hexahedron 4 nodes — DEFECT
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M109: AP209 linear_hexahedron with only 4 nodes (should be 8) */")
    lines.append("/* DEFECT: linear hex (C3D8) requires 8 corner nodes; only 4 provided */")
    lines.append("/* Element degenerates — consumers must drop or reject */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'linear_hexahedron') */")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M109: AP209 linear_hexahedron with 4 nodes not 8'),'2;1');")
    lines.append("FILE_NAME('M109.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* 4 corner nodes provided — only the bottom face of a unit cube *)  */")
    lines.append("/* A complete linear hex needs 8 corners: 4 bottom + 4 top */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(1.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(1.0,1.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(0.0,1.0,0.0));")
    lines.append("/* NODE entities — only 4 of the required 8 for a C3D8 hex */")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("#111=NODE('n2',(#101),$);")
    lines.append("#112=NODE('n3',(#102),$);")
    lines.append("#113=NODE('n4',(#103),$);")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* Byte assertion: contains(b'linear_hexahedron') */")
    lines.append("/* DEFECT: linear_hexahedron requires 8 nodes; only 4 provided */")
    lines.append("/* Cannot evaluate element as C3D8 trilinear brick with 4 nodes *)  */")
    lines.append("#200=VOLUME_3D_ELEMENT_DESCRIPTOR('lin_hex','linear_hexahedron',")
    lines.append("  (#110,#111,#112,#113));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-linear-hexahedron-4-nodes-not-8',")
    lines.append("  (#110,#111,#112,#113,#200));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M109','M109','M109',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m109(path) -> None:
    Path(path).write_text(_render_m109())


f.render = _render_m109  # type: ignore[method-assign]
f.write = _write_m109    # type: ignore[method-assign]
