"""M108 — AP238 freeform_milling_operation without surface-tolerance attribute.

Catalog claim: A FREEFORM_MILLING_OPERATION is declared without an
associated surface-deviation tolerance (chord-tolerance / scallop-height).
The CAM consumer either invents a default (often loose, leaving visible
cusps) or rejects the operation.

Reproducer recipe: FREEFORM_MILLING_OPERATION($, $, $, $, $, $) — all
optional tolerance attributes left as $.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'FREEFORM_MILLING_OPERATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M108",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 FREEFORM_MILLING_OPERATION with all "
        "surface-deviation tolerance attributes set to $ (absent); "
        "input: AP238 STEP-NC file where a FREEFORM_MILLING_OPERATION entity has "
        "chord_tolerance, scallop_height, and all other tolerance attributes omitted "
        "(each set to $) — the surface-deviation tolerance is completely unspecified; "
        "per ISO 10303-238 §5.8 freeform_milling_operation, the surface-deviation "
        "tolerance attribute must be present so the CAM consumer knows the required "
        "surface finish quality; "
        "without a tolerance the CAM consumer either invents a loose default (leaving "
        "visible cusps and staircase scallops on the finished surface) or rejects the "
        "operation entirely as ambiguous; "
        "in neither case does the consumer produce the intended surface finish; "
        "kernel must reject as ambiguous; or apply a documented default and warn "
        "that the freeform tolerance was missing and a default was substituted; "
        "synonyms: freeform tolerance missing, AP238 surface deviation unspecified, "
        "freeform milling no chord tolerance, scallop-height attribute absent, "
        "AP238 freeform op has no tolerance, STEP-NC scallop height missing, "
        "surface finish quality unspecified"
    ),
    schema="AP242",
)


def _render_m108() -> str:
    """Render AP238 file with FREEFORM_MILLING_OPERATION having all tolerance attrs as $.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       MACHINED_FEATURE 'freeform_surface_a'
      #60       MACHINING_TOOL 'ballmill_6mm'
      #70       FREEFORM_MILLING_OPERATION 'op_freeform' — DEFECT: all tolerances $
      #80       MACHINING_WORKINGSTEP 'step_freeform'
      #90       WORKPLAN 'main'
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M108: AP238 freeform_milling_operation without surface-tolerance attribute */")
    lines.append("/* DEFECT: FREEFORM_MILLING_OPERATION has all tolerance attributes set to $ */")
    lines.append("/* No chord-tolerance or scallop-height — surface finish quality unspecified */")
    lines.append("/* Violates ISO 10303-238 §5.8 freeform_milling_operation surface-tolerance requirement */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'FREEFORM_MILLING_OPERATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M108: AP238 freeform milling operation missing surface tolerance'),'2;1');")
    lines.append("FILE_NAME('M108.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('step_nc_mim');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'ap238_step_nc_mim',2007,#1);")
    lines.append("/* Standard unit context — mm */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('nc','3D'));")
    lines.append("/* Target machined feature — a freeform (sculptured) surface area */")
    lines.append("#50=MACHINED_FEATURE('freeform_surface_a',$,$,$,$,$);")
    lines.append("/* 6mm ball-end mill for freeform 5-axis milling — requires a tolerance to drive step-over */")
    lines.append("#60=MACHINING_TOOL('ballmill_6mm',$,$,$);")
    lines.append("/* Byte assertion: contains(b'FREEFORM_MILLING_OPERATION') */")
    lines.append("/* DEFECT: all tolerance / quality attributes are $ (absent) */")
    lines.append("/* chord_tolerance=$, scallop_height=$, surface_deviation=$, quality_standard=$ */")
    lines.append("/* Without any tolerance the CAM consumer cannot compute correct step-over distance *)  */")
    lines.append("#70=FREEFORM_MILLING_OPERATION('op_freeform',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("#80=MACHINING_WORKINGSTEP('step_freeform',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-freeform-milling-no-surface-tolerance',")
    lines.append("  (#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M108','M108','M108',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m108(path) -> None:
    Path(path).write_text(_render_m108())


f.render = _render_m108  # type: ignore[method-assign]
f.write = _write_m108    # type: ignore[method-assign]
