"""M118 — AP209 non-conforming mesh: tet and hex sharing a face with mismatched node counts.

Catalog claim: A linear tet (3 nodes per face) and a linear hex (4 nodes per
face) share the same geometric face. There is no MULTI_POINT_CONSTRAINT tying
the fourth hex node displacement to the tet's three nodes. The interface is
geometrically continuous but kinematically free; the solver computes separation
across the face.

Reproducer recipe: A VOLUME_3D_ELEMENT_DESCRIPTOR for a tet sharing one face
geometrically with another VOLUME_3D_ELEMENT_DESCRIPTOR hex; no MPCs tying the
extra hex node.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  count_entity_def(b'VOLUME_3D_ELEMENT_DESCRIPTOR') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M118",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 non-conforming mesh where a linear tet "
        "and a linear hex share a geometric face with mismatched node counts and no "
        "MULTI_POINT_CONSTRAINT tying the extra hex node; "
        "input: AP209 STEP file where a VOLUME_3D_ELEMENT_DESCRIPTOR for a "
        "linear_tetrahedron and a VOLUME_3D_ELEMENT_DESCRIPTOR for a linear_hexahedron "
        "share the same geometric face; the tet face has 3 nodes and the hex face has "
        "4 nodes; no MPC entity ties the 4th hex-face node displacement to the tet's "
        "three nodes; "
        "per ISO 10303-209 §6 mesh-conformity invariants, shared faces between elements "
        "of different types must be kinematically tied by MULTI_POINT_CONSTRAINT entities "
        "to ensure displacement continuity; "
        "without the MPC tying the interface is geometrically continuous but kinematically "
        "free; the solver assembles separate DOF sets on each side of the interface and "
        "computes relative separation across the shared face; structural loads transfer "
        "incorrectly and displacements diverge near the interface; "
        "kernel must detect non-conforming interfaces and either insert the necessary MPCs "
        "automatically (heal), emit a diagnostic warning, or reject as malformed; "
        "synonyms: AP209 hanging node, non-conforming interface, mesh discontinuity, "
        "AP209 non-conforming mesh, FEM tet-hex interface ungated, mesh leaks at element "
        "boundary, kinematic gap at FEM interface"
    ),
    schema="AP242",
)


def _render_m118() -> str:
    """Render AP209 file with non-conforming tet-hex interface — no MPC tying.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100-#107  CARTESIAN_POINTs (4 tet nodes + 4 extra hex nodes = 8 total)
      #110-#117  NODE entities
      #200       VOLUME_3D_ELEMENT_DESCRIPTOR for linear_tetrahedron — DEFECT partner 1
      #201       VOLUME_3D_ELEMENT_DESCRIPTOR for linear_hexahedron  — DEFECT partner 2
      #300       NODE_GROUP
      #310       FEA_MODEL
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M118: AP209 non-conforming mesh — tet-hex face with mismatched node counts */")
    lines.append("/* DEFECT: tet face (3 nodes) and hex face (4 nodes) share geometry; no MPC tying */")
    lines.append("/* Interface is kinematically free; solver computes separation across the face */")
    lines.append("/* Per AP209 §6 mesh conformity invariants, MPC is mandatory at mixed interfaces */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'VOLUME_3D_ELEMENT_DESCRIPTOR') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M118: AP209 non-conforming tet-hex mesh interface without MPC'),'2;1');")
    lines.append("FILE_NAME('M118.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Tet nodes: n1(0,0,0) n2(10,0,0) n3(5,10,0) n4(5,5,10) */")
    lines.append("/* Shared face between tet and hex: nodes n1, n2, n3 (3-node tet face) */")
    lines.append("/* Hex has a 4th node n5=(5,-5,0) on its corresponding face — no MPC for n5 */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(10.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(5.0,10.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(5.0,5.0,10.0));")
    lines.append("#104=CARTESIAN_POINT('n5',(5.0,-5.0,0.0));")
    lines.append("#105=CARTESIAN_POINT('n6',(0.0,-10.0,0.0));")
    lines.append("#106=CARTESIAN_POINT('n7',(10.0,-10.0,0.0));")
    lines.append("#107=CARTESIAN_POINT('n8',(5.0,-5.0,-10.0));")
    lines.append("#110=NODE('tet_n1',(#100),$);")
    lines.append("#111=NODE('tet_n2',(#101),$);")
    lines.append("#112=NODE('tet_n3',(#102),$);")
    lines.append("#113=NODE('tet_n4',(#103),$);")
    lines.append("#114=NODE('hex_n5',(#104),$);")
    lines.append("#115=NODE('hex_n6',(#105),$);")
    lines.append("#116=NODE('hex_n7',(#106),$);")
    lines.append("#117=NODE('hex_n8',(#107),$);")
    lines.append("/* Byte assertion: count_entity_def(b'VOLUME_3D_ELEMENT_DESCRIPTOR') >= 2 */")
    lines.append("/* DEFECT partner 1: linear tet — shared face is (n1,n2,n3), 3 nodes */")
    lines.append("#200=VOLUME_3D_ELEMENT_DESCRIPTOR('tet_elem','linear_tetrahedron',")
    lines.append("  (#110,#111,#112,#113));")
    lines.append("/* DEFECT partner 2: linear hex — corresponding face is (n1,n2,n3,n5), 4 nodes */")
    lines.append("/* n5 (#114) is the extra 4th hex-face node with NO MPC tying to tet */")
    lines.append("#201=VOLUME_3D_ELEMENT_DESCRIPTOR('hex_elem','linear_hexahedron',")
    lines.append("  (#110,#111,#114,#112,#113,#115,#116,#117));")
    lines.append("/* NO MULTI_POINT_CONSTRAINT entity tying hex node n5 to tet nodes n1,n2,n3 */")
    lines.append("/* This is the defect: the interface is kinematically free (non-conforming) */")
    lines.append("#300=NODE_GROUP('all_nodes',")
    lines.append("  (#110,#111,#112,#113,#114,#115,#116,#117),$);")
    lines.append("#310=FEA_MODEL('nonconforming_mesh',$,'',(#300),(),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-nonconforming-tet-hex-interface-no-mpc',")
    lines.append("  (#110,#111,#112,#113,#114,#115,#116,#117,#200,#201,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M118','M118','M118',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m118(path) -> None:
    Path(path).write_text(_render_m118())


f.render = _render_m118  # type: ignore[method-assign]
f.write = _write_m118    # type: ignore[method-assign]
