"""M081 — AP209 integration_point_count not consistent with element_type.

Catalog claim: An ELEMENT_REPRESENTATION for a linear_beam (which is
exactly integrated with 1-2 Gauss points) declares 5 integration points.
The over-integrated element either locks or the integration points fall in
regions of the parametric domain that don't exist for the element family.

Reproducer recipe: linear_beam CURVE_3D_ELEMENT_DESCRIPTOR paired with
ELEMENT_REPRESENTATION declaring 5 integration points.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'CURVE_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M081",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 ELEMENT_REPRESENTATION for a linear_beam "
        "with integration_point_count not consistent with element_type; "
        "input: AP209 STEP file where CURVE_3D_ELEMENT_DESCRIPTOR declares 'linear_beam' "
        "topology (exact-integration requires 1-2 Gauss points for a Euler-Bernoulli beam) "
        "but the ELEMENT_REPRESENTATION states 5 Gauss points via INTEGRATION_POINT_COUNT_NAME; "
        "per ISO 10303-209 §6 the integration-point count must match the element family's "
        "exact-integration requirement; 5 Gauss points on a linear_beam exceeds the "
        "parametric domain and causes the element to lock artificially; "
        "receivers enforcing the spec must validate integration-point count against the "
        "element family and warn-and-accept or reduce to the correct count; "
        "synonyms: over-integration, wrong Gauss rule, AP209 integration rule mismatched, "
        "Gauss points out of range, FEM element locks artificially stiff, "
        "integration_point_count vs element_type mismatch"
    ),
    schema="AP242",
)


def _render_m081() -> str:
    """Render AP209 file with linear_beam CURVE_3D_ELEMENT_DESCRIPTOR and 5 integration points.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#101 CARTESIAN_POINTs for beam end-nodes
      #110-#111 NODE entities
      #120      CURVE_3D_ELEMENT_DESCRIPTOR for linear_beam — element definition
      #200      ELEMENT_REPRESENTATION with 5 Gauss points via CONSTANT_MEASURE — defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M081: AP209 integration_point_count not consistent with element_type */")
    lines.append("/* DEFECT: linear_beam requires 1-2 Gauss points; 5 declared here */")
    lines.append("/* Over-integrated beam element locks artificially stiff */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'CURVE_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M081: AP209 linear_beam with 5 integration points not 1-2'),'2;1');")
    lines.append("FILE_NAME('M081.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Beam end-nodes: a 100mm beam along X */")
    lines.append("#100=CARTESIAN_POINT('n1',(0.0,0.0,0.0));")
    lines.append("#101=CARTESIAN_POINT('n2',(100.0,0.0,0.0));")
    lines.append("#110=NODE('n1',(#100),$);")
    lines.append("#111=NODE('n2',(#101),$);")
    lines.append("/* Byte assertion: contains(b'CURVE_3D_ELEMENT_DESCRIPTOR') */")
    lines.append("/* linear_beam: an Euler-Bernoulli beam; exact-integration needs 1-2 Gauss points */")
    lines.append("#120=CURVE_3D_ELEMENT_DESCRIPTOR('beam','linear_beam',(#110,#111));")
    lines.append("/* DEFECT: ELEMENT_REPRESENTATION states 5 integration points for linear_beam */")
    lines.append("/* INTEGRATION_POINT_COUNT_NAME('Gauss_pts') value is 5.0 — correct is 1 or 2 */")
    lines.append("/* 5 Gauss points on a linear beam: over-integration causes artificial locking */")
    lines.append("#200=ELEMENT_REPRESENTATION('beam_rep',")
    lines.append("  (CONSTANT_MEASURE(NUMERIC_MEASURE(5.0),")
    lines.append("    INTEGRATION_POINT_COUNT_NAME('Gauss_pts'))),#14);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-linear-beam-5-integration-points-not-1-2',")
    lines.append("  (#110,#111,#120,#200));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M081','M081','M081',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m081(path) -> None:
    Path(path).write_text(_render_m081())


f.render = _render_m081  # type: ignore[method-assign]
f.write = _write_m081    # type: ignore[method-assign]
