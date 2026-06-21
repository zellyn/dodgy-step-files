"""M123 — AP209 element references the same node twice in its node list.

Catalog claim: A VOLUME_3D_ELEMENT_DESCRIPTOR for a linear_tetrahedron (which
mandates 4 distinct corner nodes) lists nodes (n1, n2, n3, n2) — node 2 appears
twice. The element collapses to a degenerate triangle of zero volume. Solver
assembly produces NaN entries or skips the element silently.

Reproducer recipe: VOLUME_3D_ELEMENT_DESCRIPTOR('lin_tet',
'linear_tetrahedron', (n1,n2,n3,n2)).

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'linear_tetrahedron')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M123",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 VOLUME_3D_ELEMENT_DESCRIPTOR for a "
        "linear_tetrahedron with a duplicate node in its node list (n1,n2,n3,n2) "
        "causing a zero-volume degenerate element; "
        "input: AP209 STEP file where a VOLUME_3D_ELEMENT_DESCRIPTOR entity with "
        "element topology 'linear_tetrahedron' lists its four corner nodes as "
        "(n1, n2, n3, n2) — node n2 appears at positions 2 and 4 in the list; "
        "per ISO 10303-209 §6 element node-set uniqueness invariant, all node "
        "references within a single element's node list must be distinct; "
        "a linear tetrahedron mandates exactly 4 distinct corner nodes; "
        "repeating n2 collapses one edge of the tetrahedron to zero length; "
        "the element volume = (1/6)|det[v1-v4, v2-v4, v3-v4]| becomes zero "
        "because two column vectors of the Jacobian are identical; "
        "solver assembly of the element stiffness matrix produces a singular "
        "3x3 sub-matrix; global stiffness assembly either inserts NaN/Inf "
        "entries at the duplicated DOF or silently skips the element, "
        "leaving an unloaded zone in the mesh; "
        "kernel must validate unique node references per element and reject "
        "as malformed; "
        "synonyms: AP209 duplicate node in element, degenerate element, "
        "FEM node-list error, AP209 element repeats node, FEM element with "
        "duplicate node, tet has 3 unique nodes"
    ),
    schema="AP242",
)


def _render_m123() -> str:
    """Render AP209 file with linear_tetrahedron having duplicate node n2 at positions 2 and 4.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100-#102  CARTESIAN_POINTs (only 3 unique positions — n1, n2, n3)
      #110-#112  NODE entities (n1, n2, n3)
      #200       VOLUME_3D_ELEMENT_DESCRIPTOR('linear_tetrahedron', (n1,n2,n3,n2)) — DEFECT
      #300       NODE_GROUP
      #310       FEA_MODEL
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M123: AP209 element references the same node twice in its node list */")
    lines.append("/* DEFECT: VOLUME_3D_ELEMENT_DESCRIPTOR linear_tetrahedron node list = (n1,n2,n3,n2) */")
    lines.append("/* Node n2 appears at positions 2 and 4 — element collapses to zero volume */")
    lines.append("/* Jacobian determinant = 0; solver produces NaN stiffness or skips element */")
    lines.append("/* Per AP209 §6 all node references within an element node list must be distinct */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'linear_tetrahedron') */")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M123: AP209 linear_tetrahedron with duplicate node n2 in node list'),'2;1');")
    lines.append("FILE_NAME('M123.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Only 3 unique nodes — a valid tet would need a 4th at e.g. (5.0,5.0,10.0) */")
    lines.append("/* Node n2 is reused at position 4 in the defective element node list */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(10.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(5.0,10.0,0.0));")
    lines.append("#110=NODE('tet_n1',(#100),$);")
    lines.append("#111=NODE('tet_n2',(#101),$);")
    lines.append("#112=NODE('tet_n3',(#102),$);")
    lines.append("/* Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* Byte assertion: contains(b'linear_tetrahedron') */")
    lines.append("/* DEFECT: node list is (#110,#111,#112,#111) — #111 (n2) appears twice */")
    lines.append("/* A valid tetrahedron would list four DISTINCT nodes: (#110,#111,#112,#N4) */")
    lines.append("/* The repeated n2 collapses one tet edge to zero length; volume = 0 */")
    lines.append("#200=VOLUME_3D_ELEMENT_DESCRIPTOR('degenerate_tet','linear_tetrahedron',")
    lines.append("  (#110,#111,#112,#111));")
    lines.append("#300=NODE_GROUP('tet_nodes',(#110,#111,#112),$);")
    lines.append("#310=FEA_MODEL('duplicate_node_model',$,'',(#300),(),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-element-duplicate-node-in-list',")
    lines.append("  (#110,#111,#112,#200,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M123','M123','M123',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m123(path) -> None:
    Path(path).write_text(_render_m123())


f.render = _render_m123  # type: ignore[method-assign]
f.write = _write_m123    # type: ignore[method-assign]
