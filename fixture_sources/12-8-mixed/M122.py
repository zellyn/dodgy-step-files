"""M122 — AP209 ply orientation expressed in wrong reference frame.

Catalog claim: A composite ply's fiber-orientation vector is recorded as
global-coordinate (1,0,0) (world-X), but the solver convention is that ply
orientations are expressed in the element-local material coordinate system.
On a curved shell, global-X wraps around and rotates relative to the laminate.

Reproducer recipe: A laminate ply orientation referencing a global
AXIS2_PLACEMENT_3D with axis (0,0,1) instead of an element-attached local
frame; surface curves in 3D so the global-X interpretation is inappropriate.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'AXIS2_PLACEMENT_3D')

Tier-3: shape_null == False, n_vertices_total == 5
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M122",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 composite ply orientation "
        "AXIS2_PLACEMENT_3D expressed in global coordinates instead of the "
        "element-local material frame; fiber direction (1,0,0) is world-X but "
        "the solver expects element-local coordinates on a curved shell; "
        "input: AP209 STEP file where a laminate ply orientation references a "
        "global AXIS2_PLACEMENT_3D with Z-axis direction (0,0,1) and fiber "
        "direction (1,0,0) (world-X); the shell surface is curved in 3D so the "
        "global-X direction is not tangent to the surface at all shell elements; "
        "per ISO 10303-209 §8 composite_assembly orientation context, ply "
        "orientations must be expressed in the element-local material coordinate "
        "system where axes lie in the element plane; using a global reference frame "
        "AXIS2_PLACEMENT_3D with axis (0,0,1) is inappropriate for a curved surface; "
        "the solver reads the global-X orientation and projects it onto each element's "
        "tangent plane; on a curved shell this projection varies element by element, "
        "so fibers run across the intended path rather than along it; the composite "
        "laminate stiffness matrix is assembled incorrectly and structural predictions "
        "are wrong; "
        "kernel must warn and accept, or heal and accept: validate that the orientation "
        "reference frame matches solver convention and either warn or transform into "
        "the element-local frame; "
        "synonyms: AP209 fiber frame mismatch, ply orientation in wrong CSYS, "
        "ply vector in global vs local frame, composite orientation reference frame wrong, "
        "AP209 ply orientation frame wrong, composite fibers not aligned with surface, "
        "local vs global material direction"
    ),
    schema="AP242",
)


def _render_m122() -> str:
    """Render AP209 file with composite ply orientation in global rather than local frame.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100-#103  CARTESIAN_POINTs (4 corners of a curved-shell quad element)
      #104       CARTESIAN_POINT for global frame origin
      #105       DIRECTION for global Z axis (0,0,1)
      #106       DIRECTION for global X (fiber) direction (1,0,0)
      #107       AXIS2_PLACEMENT_3D — global frame used as ply orientation — DEFECT
      #110-#113  NODE entities
      #200       SURFACE_3D_ELEMENT_DESCRIPTOR (linear_quadrilateral shell)
      #210       PLY_LAMINATE_SEQUENCE with ply referencing global #107 — DEFECT
      #300       NODE_GROUP
      #310       FEA_MODEL
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M122: AP209 ply orientation expressed in wrong (global) reference frame */")
    lines.append("/* DEFECT: fiber direction (1,0,0) is world-X global; solver expects element-local */")
    lines.append("/* On a curved shell, global-X wraps around and fibers run off-axis */")
    lines.append("/* Per AP209 §8, ply orientation must use element-local material coordinate system */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'AXIS2_PLACEMENT_3D') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M122: AP209 composite ply orientation in global not element-local frame'),'2;1');")
    lines.append("FILE_NAME('M122.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Curved shell: nodes form a quadrilateral on a cylinder surface */")
    lines.append("/* The surface normal varies between elements — global-X wraps around */")
    lines.append("#100=CARTESIAN_POINT('cn1',(10.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('cn2',(7.07,7.07,0.0));")
    lines.append("#102=CARTESIAN_POINT('cn3',(7.07,7.07,10.0));")
    lines.append("#103=CARTESIAN_POINT('cn4',(10.0,0.0,10.0));")
    lines.append("/* Byte assertion: contains(b'AXIS2_PLACEMENT_3D') */")
    lines.append("/* DEFECT: global frame origin at world origin; axis is global Z = (0,0,1) */")
    lines.append("/* Fiber direction (1,0,0) is world-X — NOT element-local tangent direction */")
    lines.append("/* A correct ply orientation would use an element-attached local frame */")
    lines.append("#104=CARTESIAN_POINT('global_origin',(0.0,0.0,0.0));")
    lines.append("#105=DIRECTION('global_z',(0.0,0.0,1.0));")
    lines.append("#106=DIRECTION('global_x_fiber',(1.0,0.0,0.0));")
    lines.append("#107=AXIS2_PLACEMENT_3D('global_ply_frame',#104,#105,#106);")
    lines.append("#110=NODE('ply_n1',(#100),$);")
    lines.append("#111=NODE('ply_n2',(#101),$);")
    lines.append("#112=NODE('ply_n3',(#102),$);")
    lines.append("#113=NODE('ply_n4',(#103),$);")
    lines.append("#200=SURFACE_3D_ELEMENT_DESCRIPTOR('curved_shell_elem',")
    lines.append("  'linear_quadrilateral',(#110,#111,#112,#113),$);")
    lines.append("/* DEFECT: ply orientation references global #107 instead of element-local frame */")
    lines.append("/* PLY_LAMINATE_SEQUENCE with 0-degree ply in (incorrectly) global frame */")
    lines.append("#210=PLY_LAMINATE_SEQUENCE('cf_ply_0deg',#107,0.0,2.0,");  # fiber angle 0 deg, thickness 2mm
    lines.append("  'carbon_fibre_ud',1);")
    lines.append("#300=NODE_GROUP('shell_nodes',(#110,#111,#112,#113),$);")
    lines.append("#310=FEA_MODEL('curved_composite_shell',$,'',(#300),(),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-ply-orientation-wrong-reference-frame',")
    lines.append("  (#100,#101,#102,#103,#104,#105,#106,#107,")
    lines.append("   #110,#111,#112,#113,#200,#210,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M122','M122','M122',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m122(path) -> None:
    Path(path).write_text(_render_m122())


f.render = _render_m122  # type: ignore[method-assign]
f.write = _write_m122    # type: ignore[method-assign]
