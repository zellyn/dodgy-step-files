"""M080 — AP209 material property unit mismatch by 6 orders of magnitude.

Catalog claim: An elastic-property MEASURE_WITH_UNIT for Young's modulus
carries the numeric value 200000.0 (the canonical mm-MPa value for steel)
in a context whose unit is Pascals (SI). Imported as Pa, the modulus is
200 kPa instead of 200 GPa; six orders of magnitude too soft.

Reproducer recipe: MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(200000.0),
derived_unit_in_pascals) paired with a context whose LENGTH_UNIT is metre.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'DERIVED_UNIT')
  contains(b'200000.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M080",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 material property with unit mismatch "
        "by 6 orders of magnitude; "
        "input: AP209 STEP file where elastic property MEASURE_WITH_UNIT carries "
        "POSITIVE_RATIO_MEASURE(200000.0) — the canonical steel Young's modulus in mm-MPa — "
        "but the file's representation context uses SI metre LENGTH_UNIT; "
        "the DERIVED_UNIT for the modulus uses DIMENSIONAL_EXPONENTS(-1,1,-2,...) (Pascals: N/m^2) "
        "with SI metre base; imported as Pa, 200000.0 Pa = 200 kPa instead of 200 GPa; "
        "steel modulus (200 GPa = 2.0e11 Pa) off by factor of 1.0e6 — structure is 1e6x too soft; "
        "kernel must warn and accept: range-check material property values against expected "
        "order of magnitude for the named property and warn loudly on out-of-range values; "
        "synonyms: mm-MPa vs SI confusion, modulus too small, "
        "Young's modulus imported wrong, FEM material 1e6x wrong, "
        "modulus imported as Pa not MPa, AP209 material units off by million"
    ),
    schema="AP242",
)


def _render_m080() -> str:
    """Render AP209 file with Young's modulus value in mm-MPa units in a Pa context.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#12   Base SI units (metre, kilogram, second)
      #13       DIMENSIONAL_EXPONENTS for pressure/stress (Pa = kg m^-1 s^-2)
      #14-#16   DERIVED_UNIT_ELEMENTs for Pa
      #17       DERIVED_UNIT (Pa)
      #20       GEOMETRIC_REPRESENTATION_CONTEXT in SI metre
      #100      MEASURE_WITH_UNIT(200000.0, Pa) — the defect (should be 2e11 Pa for steel)
      #110      GENERAL_PROPERTY 'Youngs_Modulus'
      #120      PROPERTY_DEFINITION
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M080: AP209 material property unit mismatch by 6 orders of magnitude */")
    lines.append("/* DEFECT: Young's modulus 200000.0 is mm-MPa value, but context uses Pa (SI) */")
    lines.append("/* Imported as 200 kPa instead of 200 GPa — structure is 1e6x too soft */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'DERIVED_UNIT') */")
    lines.append("/* Byte assertion: contains(b'200000.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M080: AP209 material property unit mismatch 6 orders'),'2;1');")
    lines.append("FILE_NAME('M080.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* SI base units: metre, kilogram, second */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT($,.METRE.));")
    lines.append("#11=(MASS_UNIT()NAMED_UNIT(*)SI_UNIT(.KILO.,.GRAM.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.SECOND.)TIME_UNIT());")
    lines.append("/* DIMENSIONAL_EXPONENTS for pressure/stress: Pa = kg m^-1 s^-2 */")
    lines.append("#13=DIMENSIONAL_EXPONENTS(-1.0,1.0,-2.0,0.0,0.0,0.0,0.0);")
    lines.append("/* Byte assertion: contains(b'DERIVED_UNIT') */")
    lines.append("/* DERIVED_UNIT_ELEMENTs composing Pa = m^-1 kg^1 s^-2 */")
    lines.append("#14=DERIVED_UNIT_ELEMENT(#10,-1.0);")
    lines.append("#15=DERIVED_UNIT_ELEMENT(#11,1.0);")
    lines.append("#16=DERIVED_UNIT_ELEMENT(#12,-2.0);")
    lines.append("#17=DERIVED_UNIT((#14,#15,#16));")
    lines.append("/* Geometric context in SI metre — important: not mm */")
    lines.append("#20=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('analysis','3D'));")
    lines.append("/* Byte assertion: contains(b'200000.0') */")
    lines.append("/* DEFECT: 200000.0 is the steel modulus in mm-MPa convention (200 GPa = 200000 MPa) */")
    lines.append("/* In this file's Pa unit context: 200000.0 Pa = 200 kPa — 1e6x too small */")
    lines.append("/* Correct SI value for steel: 2.0e11 Pa = 200 GPa */")
    lines.append("#100=MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(200000.0),#17);")
    lines.append("#110=GENERAL_PROPERTY('Youngs_Modulus','Youngs_Modulus','steel');")
    lines.append("#120=PROPERTY_DEFINITION('Youngs_Modulus_def','',#110);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-material-unit-mismatch-mpa-vs-pa-6-orders',")
    lines.append("  (#100,#110,#120));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M080','M080','M080',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#20);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m080(path) -> None:
    Path(path).write_text(_render_m080())


f.render = _render_m080  # type: ignore[method-assign]
f.write = _write_m080    # type: ignore[method-assign]
