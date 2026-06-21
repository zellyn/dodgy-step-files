"""M064 — GEOMETRIC_REPRESENTATION_CONTEXT lacks UNCERTAINTY_MEASURE_WITH_UNIT.

Catalog claim: Context lacks an UNCERTAINTY_MEASURE_WITH_UNIT for length;
the reader substitutes a fixed precision constant. Models that genuinely need
a tighter or looser tolerance silently get the wrong one.

Reproducer recipe: A GEOMETRIC_REPRESENTATION_CONTEXT with no uncertainty in
its measures list; the context name is 'no_uncertainty'.

Byte assertions:
  contains(b'GEOMETRIC_REPRESENTATION_CONTEXT')
  contains(b'no_uncertainty')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M064",
    defect=(
        "GEOMETRIC_CURVE_SET in file where GEOMETRIC_REPRESENTATION_CONTEXT has no "
        "UNCERTAINTY_MEASURE_WITH_UNIT — reader-side default precision substituted; "
        "input: AP242 STEP file where the representation context uses a "
        "GLOBAL_UNIT_ASSIGNED_CONTEXT mixin (units present) but omits the "
        "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT mixin, so no UNCERTAINTY_MEASURE_WITH_UNIT "
        "is declared for length precision; "
        "AP203/242 require UNCERTAINTY_MEASURE_WITH_UNIT to be present in the context "
        "so consumers know the file's declared model precision; "
        "without it, OCCT substitutes read.precision.val (default 0.0001 mm); "
        "models needing tighter tolerance (e.g. 1e-7) are silently healed at 1e-4, "
        "causing geometry joins to fail; models needing looser tolerance are also wrong; "
        "kernel must heal and accept: compute uncertainty from geometry-extent and entity "
        "tolerances; warn that no uncertainty was declared; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: uncertainty defaulted, precision guessed, no tolerance in file, "
        "kernel-default precision used, UNCERTAINTY_MEASURE missing"
    ),
    schema="AP242",
)


def _render_m064() -> str:
    """Render AP242 file with GEOMETRIC_REPRESENTATION_CONTEXT missing UNCERTAINTY_MEASURE_WITH_UNIT.

    Entity layout:
      #10  LENGTH_UNIT (complex)
      #11  PLANE_ANGLE_UNIT (complex)
      #12  SOLID_ANGLE_UNIT (complex)
      #13  GEOMETRIC_REPRESENTATION_CONTEXT with no uncertainty — the defect
           Context name 'no_uncertainty' satisfies contains(b'no_uncertainty').
           No UNCERTAINTY_MEASURE_WITH_UNIT anywhere in file:
           count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 0
      #20  CARTESIAN_POINT origin
      #21  CARTESIAN_POINT end
      #22  DIRECTION z_axis
      #23  DIRECTION x_axis
      #24  AXIS2_PLACEMENT_3D
      #25  CIRCLE
      #26  GEOMETRIC_CURVE_SET (model entity)
      #30+ PRODUCT chain (no UNCERTAINTY_MEASURE_WITH_UNIT injected — manual chain)
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M064: GEOMETRIC_REPRESENTATION_CONTEXT missing UNCERTAINTY_MEASURE_WITH_UNIT */")
    lines.append("/* DEFECT: no GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT mixin; reader defaults precision */")
    lines.append("/* count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 0 throughout file */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M064: GEOMETRIC_REPRESENTATION_CONTEXT missing UNCERTAINTY_MEASURE_WITH_UNIT'),'2;1');")
    lines.append("FILE_NAME('M064.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Unit declarations — present, but UNCERTAINTY_MEASURE_WITH_UNIT is absent */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("/* Context with units but NO uncertainty — the defect */")
    lines.append("/* Byte assertion: contains(b'GEOMETRIC_REPRESENTATION_CONTEXT') */")
    lines.append("/* Byte assertion: contains(b'no_uncertainty') */")
    lines.append("#13=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('no_uncertainty','3D'));")
    lines.append("/* Geometry */")
    lines.append("#20=CARTESIAN_POINT('origin',(0.,0.,0.));")
    lines.append("#21=CARTESIAN_POINT('end',(50.,0.,0.));")
    lines.append("#22=DIRECTION('z_axis',(0.,0.,1.));")
    lines.append("#23=DIRECTION('x_axis',(1.,0.,0.));")
    lines.append("#24=AXIS2_PLACEMENT_3D('placement',#20,#22,#23);")
    lines.append("#25=CIRCLE('edge_circle',#24,25.);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#26=GEOMETRIC_CURVE_SET('geometric-context-missing-uncertainty-measure-with-unit',(#24,#25,#20,#21));")
    lines.append("/* Minimal PRODUCT chain — no UNCERTAINTY_MEASURE_WITH_UNIT emitted */")
    lines.append("#30=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#31=PRODUCT_CONTEXT('',#30,'mechanical');")
    lines.append("#32=PRODUCT('M064','M064','M064',(#31));")
    lines.append("#33=PRODUCT_DEFINITION_FORMATION('','',#32);")
    lines.append("#34=PRODUCT_DEFINITION_CONTEXT(#30,'design');")
    lines.append("#35=PRODUCT_DEFINITION('','',#33,#34);")
    lines.append("#36=PRODUCT_DEFINITION_SHAPE('','',#35);")
    lines.append("#37=SHAPE_REPRESENTATION('',(#26),#13);")
    lines.append("#38=SHAPE_DEFINITION_REPRESENTATION(#36,#37);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m064(path) -> None:
    Path(path).write_text(_render_m064())


f.render = _render_m064  # type: ignore[method-assign]
f.write = _write_m064    # type: ignore[method-assign]
