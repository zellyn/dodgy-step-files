"""M119 — AP209 shell element with zero plate thickness.

Catalog claim: A SURFACE_3D_ELEMENT_DESCRIPTOR for a linear_quadrilateral shell
carries an associated thickness measure of 0.0. Bending stiffness
K = E*t³/12(1-v²) collapses to zero. Out-of-plane deflections diverge.
POSITIVE_LENGTH_MEASURE(0.0) is itself schema-illegal — POSITIVE means > 0.

Reproducer recipe: A surface element descriptor whose thickness
MEASURE_WITH_UNIT carries POSITIVE_LENGTH_MEASURE(0.0).

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'SURFACE_3D_ELEMENT_DESCRIPTOR')
  contains(b'POSITIVE_LENGTH_MEASURE(0.0)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M119",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 SURFACE_3D_ELEMENT_DESCRIPTOR for a "
        "linear_quadrilateral shell element with associated thickness "
        "POSITIVE_LENGTH_MEASURE(0.0), which is schema-illegal and causes bending "
        "stiffness to collapse to zero; "
        "input: AP209 STEP file where a SURFACE_3D_ELEMENT_DESCRIPTOR for a "
        "linear_quadrilateral shell references a thickness MEASURE_WITH_UNIT carrying "
        "POSITIVE_LENGTH_MEASURE(0.0); "
        "per ISO 10303-209 §6 surface_3d_element_descriptor thickness positivity "
        "constraint, the POSITIVE_LENGTH_MEASURE attribute type mandates a strictly "
        "positive value (> 0); a value of 0.0 violates the type constraint; "
        "bending stiffness K = E*t^3 / (12*(1 - v^2)) collapses to zero when t=0; "
        "an FEA solver using this shell element produces a singular stiffness matrix "
        "for bending DOFs; out-of-plane deflections diverge and the global assembly "
        "fails or yields NaN displacements; "
        "kernel must reject zero thickness or warn and substitute a minimum positive "
        "thickness; "
        "synonyms: zero-thickness shell, AP209 plate degenerate, shell element zero "
        "thickness, FEM plate has no bending stiffness, shell thickness missing, "
        "AP209 shell zero thickness, shell thickness measure is 0"
    ),
    schema="AP242",
)


def _render_m119() -> str:
    """Render AP209 file with SURFACE_3D_ELEMENT_DESCRIPTOR carrying POSITIVE_LENGTH_MEASURE(0.0).

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100-#103  CARTESIAN_POINTs (4 corners of a unit-square shell)
      #110-#113  NODE entities
      #200       SURFACE_3D_ELEMENT_DESCRIPTOR ('linear_quadrilateral') — with zero thickness
      #210       MEASURE_WITH_UNIT carrying POSITIVE_LENGTH_MEASURE(0.0) — DEFECT
      #300       NODE_GROUP
      #310       FEA_MODEL
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M119: AP209 shell element with zero plate thickness */")
    lines.append("/* DEFECT: SURFACE_3D_ELEMENT_DESCRIPTOR thickness = POSITIVE_LENGTH_MEASURE(0.0) */")
    lines.append("/* Schema-illegal: POSITIVE means > 0; bending stiffness collapses to zero */")
    lines.append("/* K = E*t^3 / 12(1-v^2) = 0 when t=0; stiffness matrix is singular */")
    lines.append("/* Per AP209 §6 surface_3d_element_descriptor thickness positivity constraint */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'SURFACE_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* Byte assertion: contains(b'POSITIVE_LENGTH_MEASURE(0.0)') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M119: AP209 shell element with zero plate thickness POSITIVE_LENGTH_MEASURE(0.0)'),'2;1');")
    lines.append("FILE_NAME('M119.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Four corners of a unit-square shell in the XY-plane */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(10.0,0.0,0.0));")
    lines.append("#102=CARTESIAN_POINT('n3',(10.0,10.0,0.0));")
    lines.append("#103=CARTESIAN_POINT('n4',(0.0,10.0,0.0));")
    lines.append("#110=NODE('shell_n1',(#100),$);")
    lines.append("#111=NODE('shell_n2',(#101),$);")
    lines.append("#112=NODE('shell_n3',(#102),$);")
    lines.append("#113=NODE('shell_n4',(#103),$);")
    lines.append("/* Byte assertion: contains(b'SURFACE_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* Byte assertion: contains(b'POSITIVE_LENGTH_MEASURE(0.0)') */")
    lines.append("/* DEFECT: thickness is POSITIVE_LENGTH_MEASURE(0.0) — schema-illegal zero value */")
    lines.append("/* A valid shell would have e.g. POSITIVE_LENGTH_MEASURE(2.5) */")
    lines.append("#210=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.0),#10);")
    lines.append("#200=SURFACE_3D_ELEMENT_DESCRIPTOR('zero_thickness_shell',")
    lines.append("  'linear_quadrilateral',(#110,#111,#112,#113),#210);")
    lines.append("#300=NODE_GROUP('shell_nodes',(#110,#111,#112,#113),$);")
    lines.append("#310=FEA_MODEL('zero_thickness_shell_model',$,'',(#300),(),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-shell-element-zero-plate-thickness',")
    lines.append("  (#110,#111,#112,#113,#200,#210,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M119','M119','M119',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m119(path) -> None:
    Path(path).write_text(_render_m119())


f.render = _render_m119  # type: ignore[method-assign]
f.write = _write_m119    # type: ignore[method-assign]
