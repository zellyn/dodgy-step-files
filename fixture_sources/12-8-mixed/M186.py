"""M186 — AP238 coolant type incompatible with workpiece material

Catalog claim: A COOLANT_OPERATION declares coolant type WATER on a workpiece
whose material is declared as MAGNESIUM. Water on burning magnesium accelerates
the fire (hydrogen liberation); shop safety codes prohibit this combination.

Reproducer recipe: a WORKPIECE with MATERIAL('AZ31_magnesium', ..); a
COOLANT_OPERATION with mode .WATER. targeting that workpiece.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'COOLANT_OPERATION')
  contains(b'magnesium')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M186",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where COOLANT_OPERATION "
        "declares coolant type WATER on a workpiece whose material is MAGNESIUM; "
        "input: AP238 STEP-NC file containing a WORKPLAN with a coolant operation; "
        "the WORKPIECE 'magnesium_block' is declared with MATERIAL('AZ31_magnesium', ...); "
        "AZ31 magnesium alloy: reacts violently with water when ignited, liberating hydrogen gas; "
        "the COOLANT_OPERATION 'water_coolant_op' declares coolant mode .WATER. targeting the workpiece; "
        "water on burning magnesium accelerates the fire — hydrogen liberation causes explosion risk; "
        "OSHA/NFPA shop-safety guidance prohibits water coolant on magnesium workpieces; "
        "per ISO 10303-238 §5.8 coolant_operation material-compatibility safety rule: "
        "kernel must cross-check coolant type against workpiece material; "
        "kernel must reject incompatible safety-critical coolant-material combinations; "
        "synonyms: AP238 unsafe coolant choice, STEP-NC water on Mg, "
        "coolant material incompatibility, AP238 coolant unsafe for material, "
        "STEP-NC water on magnesium, incompatible coolant type, "
        "AP238 water on magnesium, STEP-NC unsafe coolant, coolant type wrong for material"
    ),
    schema="AP242",
)


def _render_m186() -> str:
    """Render AP238 STEP-NC file with COOLANT_OPERATION using WATER on MAGNESIUM workpiece.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       MATERIAL 'AZ31_magnesium' — magnesium alloy, incompatible with water
      #40       WORKPIECE 'magnesium_block' — made of AZ31 magnesium
      #50       COOLANT_OPERATION 'water_coolant_op' — DEFECT: mode .WATER. on Mg workpiece
      #60       MACHINING_WORKINGSTEP 'coolant_step'
      #70       WORKPLAN 'unsafe_coolant_program'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M186: AP238 coolant type WATER incompatible with MAGNESIUM workpiece material */")
    lines.append("/* DEFECT: COOLANT_OPERATION declares mode .WATER. on AZ31 magnesium workpiece */")
    lines.append("/* Water on burning magnesium liberates hydrogen gas — explosion/fire risk */")
    lines.append("/* OSHA/NFPA shop-safety guidance prohibits water coolant on magnesium */")
    lines.append("/* Per ISO 10303-238 §5.8 coolant_operation material-compatibility safety rule */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'COOLANT_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'magnesium') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M186: AP238 COOLANT_OPERATION WATER mode on AZ31 magnesium workpiece'),'2;1');")
    lines.append("FILE_NAME('M186.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* mm length unit reference for MEASURE_WITH_UNIT */")
    lines.append("#15=SI_UNIT(.MILLI.,.METRE.);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-coolant-water-on-magnesium-workpiece',")
    lines.append("  (#30,#40,#50,#60));")
    lines.append("/* MATERIAL 'AZ31_magnesium': magnesium alloy — reacts violently with water when ignited */")
    lines.append("/* Byte assertion: contains(b'magnesium') */")
    lines.append("#30=MATERIAL('AZ31_magnesium','AZ31B magnesium alloy workpiece material',$);")
    lines.append("/* WORKPIECE 'magnesium_block': made of AZ31 magnesium alloy */")
    lines.append("#40=WORKPIECE('magnesium_block','AZ31 magnesium alloy block',$,#30,$,$,$);")
    lines.append("/* Byte assertion: contains(b'COOLANT_OPERATION') */")
    lines.append("/* DEFECT: COOLANT_OPERATION 'water_coolant_op' uses .WATER. mode on Mg workpiece */")
    lines.append("/* Water on burning magnesium: hydrogen liberation + fire acceleration */")
    lines.append("#50=COOLANT_OPERATION('water_coolant_op',.WATER.,$,#40,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'coolant_step' */")
    lines.append("#60=MACHINING_WORKINGSTEP('coolant_step','Water coolant on magnesium step',#50,#40,$);")
    lines.append("/* WORKPLAN: unsafe coolant operation on magnesium workpiece */")
    lines.append("#70=WORKPLAN('unsafe_coolant_program','Unsafe water coolant on Mg workplan',(),$,(#60));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M186','M186','M186',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m186(path) -> None:
    Path(path).write_text(_render_m186())


f.render = _render_m186  # type: ignore[method-assign]
f.write = _write_m186    # type: ignore[method-assign]
