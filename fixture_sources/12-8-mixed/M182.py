"""M182 — AP238 setup_instruction sequence with non-monotonic time stamps

Catalog claim: A sequence of SETUP_INSTRUCTION entities (mount fixture,
locate workpiece, tighten clamps) carries time_stamps in non-monotonic
order: instruction A at 09:00, B at 08:30, C at 09:15. Either the
publisher copied stamps from a different job or the operator instructions
were re-ordered without updating times.

Reproducer recipe: three SETUP_INSTRUCTION entities with timestamps
2026-05-02T09:00:00, 2026-05-02T08:30:00, 2026-05-02T09:15:00
(non-monotonic).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'SETUP_INSTRUCTION')
  contains(b'2026-05-02T09:00:00')
  contains(b'2026-05-02T08:30:00')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M182",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where SETUP_INSTRUCTION entities "
        "carry non-monotonic time stamps in their declared sequence; "
        "input: AP238 STEP-NC file containing a WORKPLAN with three SETUP_INSTRUCTION steps; "
        "instruction 'mount_fixture' has timestamp '2026-05-02T09:00:00'; "
        "instruction 'locate_workpiece' has timestamp '2026-05-02T08:30:00' — DEFECT: goes backward; "
        "instruction 'tighten_clamps' has timestamp '2026-05-02T09:15:00'; "
        "time stamps are non-monotonic: 09:00 -> 08:30 -> 09:15 — second step goes backward in time; "
        "either publisher copied stamps from different job or steps were re-ordered without updating times; "
        "per ISO 10303-238 §5.4 setup_instruction chronology rule and ISO 8601 ordering: "
        "time stamps in a setup-instruction sequence must be monotonically increasing; "
        "kernel must validate timestamp monotonicity along setup-instruction sequence; "
        "synonyms: AP238 setup steps out of order, STEP-NC setup timestamps wrong, "
        "operator instructions go backward in time, AP238 setup-instruction order wrong, "
        "STEP-NC setup timestamps backwards, operator step time goes back, "
        "AP238 setup-instruction time inversion, STEP-NC operator steps non-monotonic, "
        "setup chronology wrong, instruction timestamps decreasing"
    ),
    schema="AP242",
)


def _render_m182() -> str:
    """Render AP238 STEP-NC file with SETUP_INSTRUCTION non-monotonic timestamps.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #40       SETUP_INSTRUCTION 'mount_fixture'    — timestamp 2026-05-02T09:00:00 (first)
      #41       SETUP_INSTRUCTION 'locate_workpiece' — timestamp 2026-05-02T08:30:00 (DEFECT: backward)
      #42       SETUP_INSTRUCTION 'tighten_clamps'   — timestamp 2026-05-02T09:15:00 (third)
      #50       WORKPLAN 'non_monotonic_setup_program'
      #51       SETUP 'machine_setup' — references the three instructions
      #60       WORKPIECE 'setup_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M182: AP238 setup_instruction sequence with non-monotonic time stamps */")
    lines.append("/* DEFECT: timestamps 09:00 -> 08:30 -> 09:15 are non-monotonic */")
    lines.append("/* Instruction 'locate_workpiece' at 08:30 goes backward from 'mount_fixture' 09:00 */")
    lines.append("/* Publisher copied stamps from different job or steps re-ordered without update */")
    lines.append("/* Per ISO 10303-238 §5.4 and ISO 8601: setup-instruction timestamps must be monotonic */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'SETUP_INSTRUCTION') */")
    lines.append("/* Byte assertion: contains(b'2026-05-02T09:00:00') */")
    lines.append("/* Byte assertion: contains(b'2026-05-02T08:30:00') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M182: AP238 setup_instruction non-monotonic timestamps'),'2;1');")
    lines.append("FILE_NAME('M182.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-setup-instruction-non-monotonic-timestamps',")
    lines.append("  (#51,#60));")
    lines.append("/* Byte assertion: contains(b'SETUP_INSTRUCTION') */")
    lines.append("/* Step 1: mount_fixture at 09:00 — first step, valid starting time */")
    lines.append("/* Byte assertion: contains(b'2026-05-02T09:00:00') */")
    lines.append("#40=SETUP_INSTRUCTION('mount_fixture','Mount fixture on machine table','2026-05-02T09:00:00',$);")
    lines.append("/* DEFECT: locate_workpiece at 08:30 — goes BACKWARD from mount_fixture at 09:00 */")
    lines.append("/* Byte assertion: contains(b'2026-05-02T08:30:00') */")
    lines.append("#41=SETUP_INSTRUCTION('locate_workpiece','Locate workpiece in fixture','2026-05-02T08:30:00',$);")
    lines.append("/* Step 3: tighten_clamps at 09:15 — forward from step 1 but after backward step 2 */")
    lines.append("#42=SETUP_INSTRUCTION('tighten_clamps','Tighten workpiece clamps','2026-05-02T09:15:00',$);")
    lines.append("/* WORKPIECE 'setup_workpiece' */")
    lines.append("#60=WORKPIECE('setup_workpiece','Workpiece for non-monotonic setup test',$,$,$,$,$);")
    lines.append("/* SETUP 'machine_setup' references all three setup instructions in declared order */")
    lines.append("/* Declared sequence: #40 (09:00), #41 (08:30), #42 (09:15) — DEFECT: non-monotonic */")
    lines.append("#51=SETUP('machine_setup',$,$,(#40,#41,#42),#60);")
    lines.append("/* WORKPLAN: non-monotonic setup followed by no operations */")
    lines.append("#50=WORKPLAN('non_monotonic_setup_program','Non-monotonic setup instruction workplan',(),$,());")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M182','M182','M182',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m182(path) -> None:
    Path(path).write_text(_render_m182())


f.render = _render_m182  # type: ignore[method-assign]
f.write = _write_m182    # type: ignore[method-assign]
