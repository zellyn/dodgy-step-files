"""M082 — AP209 surface element node order is clockwise (negative Jacobian).

Catalog claim: A SURFACE_3D_ELEMENT_DESCRIPTOR for a linear_quadrilateral
lists its corner nodes in clockwise order when viewed from the surface
normal (CCW is the convention). The element's Jacobian determinant is
negative everywhere; integral computations come out with reversed sign.

Reproducer recipe: A planar-square quad with corners (0,0)(1,0)(1,1)(0,1)
listed in order n1,n4,n3,n2 (clockwise).

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'SURFACE_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M082",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 SURFACE_3D_ELEMENT_DESCRIPTOR for a "
        "linear_quadrilateral with corner nodes listed in clockwise order (negative Jacobian); "
        "input: AP209 STEP file where SURFACE_3D_ELEMENT_DESCRIPTOR declares a unit-square "
        "quad element whose corner nodes are given as n1(0,0), n4(0,1), n3(1,1), n2(1,0) — "
        "clockwise winding when viewed from the +Z surface normal; "
        "ISO 10303-209 §6 mandates counter-clockwise node ordering when viewed from the "
        "outward surface normal; with CW ordering the Jacobian determinant is negative "
        "everywhere in the element domain — integration produces sign-reversed results; "
        "receivers enforcing the spec must detect negative Jacobian, reject the element, "
        "reverse the node order, or warn the consumer that downstream integral signs may be "
        "inverted; kernel must never silently integrate a negative-Jacobian element; "
        "synonyms: negative Jacobian element, wound backwards, element flipped, "
        "FEM element has negative Jacobian, quad winding wrong, AP209 reversed element"
    ),
    schema="AP242",
)


def _render_m082() -> str:
    """Render AP209 file with linear_quadrilateral nodes in clockwise order.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#103 CARTESIAN_POINTs: (0,0), (1,0), (1,1), (0,1) — CCW corners
      #110-#113 NODE entities for the 4 corners
      #120      SURFACE_3D_ELEMENT_DESCRIPTOR with CW order n1,n4,n3,n2 — defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M082: AP209 surface element node order is clockwise (negative Jacobian) */")
    lines.append("/* DEFECT: linear_quadrilateral nodes listed CW: n1(0,0),n4(0,1),n3(1,1),n2(1,0) */")
    lines.append("/* CCW convention: n1(0,0),n2(1,0),n3(1,1),n4(0,1) */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'SURFACE_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M082: AP209 linear_quadrilateral with clockwise node order'),'2;1');")
    lines.append("FILE_NAME('M082.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Unit-square quad corners */")
    lines.append("/* n1=(0,0,0) n2=(1,0,0) n3=(1,1,0) n4=(0,1,0) in geometric CCW order */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(1.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(1.0,1.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(0.0,1.0,0.0));")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("#111=NODE('n2',(#101),$);")
    lines.append("#112=NODE('n3',(#102),$);")
    lines.append("#113=NODE('n4',(#103),$);")
    lines.append("/* Byte assertion: contains(b'SURFACE_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* DEFECT: node list is n1,n4,n3,n2 — clockwise winding, negative Jacobian */")
    lines.append("/* CCW convention would be n1,n2,n3,n4 */")
    lines.append("/* Clockwise: (0,0) -> (0,1) -> (1,1) -> (1,0) viewed from +Z */")
    lines.append("#120=SURFACE_3D_ELEMENT_DESCRIPTOR('quad','linear_quadrilateral',")
    lines.append("  (#110,#113,#112,#111));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-linear-quadrilateral-clockwise-negative-jacobian',")
    lines.append("  (#110,#111,#112,#113,#120));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M082','M082','M082',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m082(path) -> None:
    Path(path).write_text(_render_m082())


f.render = _render_m082  # type: ignore[method-assign]
f.write = _write_m082    # type: ignore[method-assign]
