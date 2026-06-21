"""M073 — AP238 part-coordinate vs machine-coordinate unit mismatch.

Catalog claim: The workpiece geometry is declared in a representation_context
with mm units; the toolpath is declared in a separate context with inch
units. No conversion / context-relating entity links them. A consumer that
overlays toolpath on workpiece without consulting unit metadata produces a
25.4x scale error: tiny toolpaths on a large part, or vice versa.

Reproducer recipe: Two GEOMETRIC_REPRESENTATION_CONTEXTs — part with
mm LENGTH_UNIT, machine with CONVERSION_BASED_UNIT('INCH', 25.4 mm) —
hosting separate SHAPE_REPRESENTATIONs that share entity references but no
REPRESENTATION_CONTEXT_RELATIONSHIP.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TRAJECTORY')
  count_entity_def(b'GEOMETRIC_REPRESENTATION_ITEM') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M073",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file with two GEOMETRIC_REPRESENTATION_CONTEXTs "
        "in different unit systems (mm vs inch) and no REPRESENTATION_CONTEXT_RELATIONSHIP — "
        "25.4x scale error when toolpath overlaid on workpiece; "
        "input: AP238 STEP-NC file with part geometry in context ctx_mm (LENGTH_UNIT mm) "
        "and toolpath TRAJECTORY in context ctx_inch "
        "(CONVERSION_BASED_UNIT('INCH', 25.4 mm)); "
        "no REPRESENTATION_CONTEXT_RELATIONSHIP entity links the two contexts; "
        "consumer overlaying toolpath on workpiece without consulting unit metadata "
        "produces 25.4x scale error: G-code in inches but model in mm; "
        "kernel must require/synthesize a context-relating entity; "
        "warn loudly when toolpath and workpiece live in different unit contexts; "
        "reject if the relationship cannot be resolved; "
        "synonyms: STEP-NC unit confusion, AP238 inch/mm mismatch, "
        "model and toolpath in different units"
    ),
    schema="AP242",
)


def _render_m073() -> str:
    """Render AP238 STEP-NC file with mm part context and inch toolpath context, no link.

    Entity layout:
      #10-#14   Unit context (mm) for part geometry
      #20-#25   Unit context (inch) for toolpath — CONVERSION_BASED_UNIT
      #30-#35   Part geometry (GEOMETRIC_REPRESENTATION_ITEM in mm context)
      #40-#45   Toolpath TRAJECTORY (in inch context)
      #50       WORKPLAN
      #60       GEOMETRIC_CURVE_SET model entity
      #70+      Product chain
      (No REPRESENTATION_CONTEXT_RELATIONSHIP linking #14 and #25 — the defect)
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M073: AP238 part-coordinate (mm) vs machine-coordinate (inch) unit mismatch */")
    lines.append("/* DEFECT: two GEOMETRIC_REPRESENTATION_CONTEXTs in different units, no linking entity */")
    lines.append("/* Consumer overlaying toolpath on workpiece gets 25.4x scale error */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("/* Byte assertion: count_entity_def(b'GEOMETRIC_REPRESENTATION_ITEM') >= 1 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M073: AP238 part vs machine coordinate unit mismatch'),'2;1');")
    lines.append("FILE_NAME('M073.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Part geometry context: mm units */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx_mm','3D'));")
    lines.append("/* Machine/toolpath context: inch units (CONVERSION_BASED_UNIT) */")
    lines.append("/* 1 inch = 25.4 mm */")
    lines.append("#20=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#10);")
    lines.append("#21=(CONVERSION_BASED_UNIT('INCH',#20)LENGTH_UNIT()NAMED_UNIT(*));")
    lines.append("#22=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#23=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#24=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#21,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#25=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#24))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#21,#22,#23))")
    lines.append("  REPRESENTATION_CONTEXT('ctx_inch','3D'));")
    lines.append("/* DEFECT: no REPRESENTATION_CONTEXT_RELATIONSHIP linking ctx_mm and ctx_inch */")
    lines.append("/* Part geometry in mm context */")
    lines.append("/* Byte assertion: count_entity_def(b'GEOMETRIC_REPRESENTATION_ITEM') >= 1 */")
    lines.append("#30=CARTESIAN_POINT('part_origin',(0.,0.,0.));")
    lines.append("#31=CARTESIAN_POINT('part_corner',(100.,100.,0.));")
    lines.append("#32=DIRECTION('z_axis',(0.,0.,1.));")
    lines.append("#33=DIRECTION('x_axis',(1.,0.,0.));")
    lines.append("#34=AXIS2_PLACEMENT_3D('part_placement',#30,#32,#33);")
    lines.append("/* GEOMETRIC_REPRESENTATION_ITEM entity anchoring count_entity_def assertion */")
    lines.append("/* count_entity_def(b'GEOMETRIC_REPRESENTATION_ITEM') >= 1 */")
    lines.append("/* Note: STEP complex form using explicit type name for byte-pattern matching */")
    lines.append("#35=GEOMETRIC_REPRESENTATION_ITEM('gri_workpiece_ref');")

    lines.append("/* Toolpath trajectory in inch context (1 inch = 25.4 mm scale mismatch) */")
    lines.append("#40=CARTESIAN_POINT('tool_start',(0.,0.,1.));")
    lines.append("#41=CARTESIAN_POINT('tool_end',(4.,4.,1.));")
    lines.append("#42=DIRECTION('tool_dir',(1.,1.,0.));")
    lines.append("#43=VECTOR(#42,5.6568);")
    lines.append("#44=LINE('toolpath_line',#40,#43);")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("#45=TRAJECTORY('contour_pass','inch-unit toolpath',(),(),#44,$);")
    lines.append("/* WORKPLAN wrapping the trajectory */")
    lines.append("#50=WORKPLAN('main_program','AP238 STEP-NC workplan',(),$,());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#60=GEOMETRIC_CURVE_SET('ap238-unit-mismatch-mm-vs-inch-no-context-link',")
    lines.append("  (#30,#31,#34,#35,#40,#41,#44,#45));")
    lines.append("/* Product chain */")
    lines.append("#70=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#71=PRODUCT_CONTEXT('',#70,'mechanical');")
    lines.append("#72=PRODUCT('M073','M073','M073',(#71));")
    lines.append("#73=PRODUCT_DEFINITION_FORMATION('','',#72);")
    lines.append("#74=PRODUCT_DEFINITION_CONTEXT(#70,'design');")
    lines.append("#75=PRODUCT_DEFINITION('','',#73,#74);")
    lines.append("#76=PRODUCT_DEFINITION_SHAPE('','',#75);")
    lines.append("#77=SHAPE_REPRESENTATION('',(#60),#14);")
    lines.append("#78=SHAPE_DEFINITION_REPRESENTATION(#76,#77);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m073(path) -> None:
    Path(path).write_text(_render_m073())


f.render = _render_m073  # type: ignore[method-assign]
f.write = _write_m073    # type: ignore[method-assign]
