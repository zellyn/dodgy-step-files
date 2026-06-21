"""M178 — AP238 inspection_probing path passes through workpiece body

Catalog claim: An INSPECTION_PROBING op's approach segment runs from
the probe-storage position straight through the workpiece body to reach
the touch point. The probe stylus shears or breaks.

Reproducer recipe: an INSPECTION_PROBING op whose probe path POLYLINE
runs from (50,50,200) to (50,50,-5) while the workpiece body occupies
the box (0..100, 0..100, 0..50).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'INSPECTION_PROBING(')
  contains(b'probe_path_through_part')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M178",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where INSPECTION_PROBING op approach "
        "segment runs straight through the workpiece body to reach the touch point; "
        "input: AP238 STEP-NC file containing a WORKPLAN for an inspection probing operation; "
        "the WORKPIECE 'inspection_block' occupies the box (0..100, 0..100, 0..50); "
        "the INSPECTION_PROBING 'probe_collision_op' has a probe path POLYLINE "
        "named 'probe_path_through_part' running from (50,50,200) to (50,50,-5); "
        "the path segment from (50,50,200) descends through the workpiece box "
        "(entering at z=50, passing through body, exiting below at z=-5 which is below bottom); "
        "the probe stylus shears or breaks when it hits the workpiece body; "
        "a safe approach must detour around the workpiece before touching the measurement point; "
        "per ISO 10303-238 §6.2 inspection probing safe-approach invariant: "
        "probe paths must be collision-free with respect to the workpiece envelope; "
        "kernel must collision-check probe paths against workpiece envelope and reject or warn; "
        "synonyms: AP238 probe collision, STEP-NC inspection path crashes, "
        "probe stylus shears, inspection trajectory through workpiece, "
        "AP238 probe crashes into part, STEP-NC inspection path collides, stylus shears off"
    ),
    schema="AP242",
)


def _render_m178() -> str:
    """Render AP238 STEP-NC file with INSPECTION_PROBING path through workpiece body.

    Entity layout:
      #10-#14   Unit context (mm)
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       CARTESIAN_POINT (50,50,200) — probe storage position (above part)
      #31       CARTESIAN_POINT (50,50,-5) — probe target (below part bottom face)
      #32       POLYLINE 'probe_path_through_part' — DEFECT: passes through workpiece body
      #50       WORKPLAN 'probe_collision_program' — AP238 top-level NC program
      #51       MACHINING_WORKINGSTEP 'probe_collision_step'
      #52       INSPECTION_PROBING 'probe_collision_op' — DEFECT: path through workpiece
      #60       WORKPIECE 'inspection_block' — occupies (0..100, 0..100, 0..50)
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M178: AP238 inspection_probing path passes through workpiece body */")
    lines.append("/* DEFECT: INSPECTION_PROBING probe path POLYLINE runs (50,50,200) to (50,50,-5) */")
    lines.append("/* Workpiece 'inspection_block' occupies box (0..100, 0..100, 0..50) */")
    lines.append("/* Probe descends from z=200 through workpiece top face (z=50) to z=-5 */")
    lines.append("/* Probe stylus shears against workpiece body — safe approach required */")
    lines.append("/* Per ISO 10303-238 §6.2 probe paths must be collision-free with workpiece envelope */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'INSPECTION_PROBING(') */")
    lines.append("/* Byte assertion: contains(b'probe_path_through_part') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M178: AP238 inspection_probing path through workpiece body'),'2;1');")
    lines.append("FILE_NAME('M178.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Probe path points: from storage position straight through workpiece body */")
    lines.append("#30=CARTESIAN_POINT('probe_storage',(50.0,50.0,200.0));")
    lines.append("#31=CARTESIAN_POINT('probe_target',(50.0,50.0,-5.0));")
    lines.append("/* Byte assertion: contains(b'probe_path_through_part') */")
    lines.append("/* DEFECT: POLYLINE descends from (50,50,200) through workpiece body to (50,50,-5) */")
    lines.append("/* Workpiece top face is at z=50; probe enters body at z=50, exits below z=0 */")
    lines.append("#32=POLYLINE('probe_path_through_part',(#30,#31));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-inspection-probing-path-through-workpiece-body',")
    lines.append("  (#32,#52,#60));")
    lines.append("/* Byte assertion: contains(b'INSPECTION_PROBING(') */")
    lines.append("/* DEFECT: INSPECTION_PROBING op whose approach path runs through workpiece */")
    lines.append("#52=INSPECTION_PROBING('probe_collision_op',$,#32,$,$,$);")
    lines.append("/* WORKPIECE 'inspection_block': occupies box (0..100, 0..100, 0..50) */")
    lines.append("/* Probe path (50,50,200)->(50,50,-5) passes through this body */")
    lines.append("#60=WORKPIECE('inspection_block','Inspection block workpiece (0..100 0..100 0..50)',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'probe_collision_step' links op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('probe_collision_step','Probe collision workingstep',#52,#60,$);")
    lines.append("/* WORKPLAN: single inspection step with colliding probe path */")
    lines.append("#50=WORKPLAN('probe_collision_program','Probe collision inspection workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M178','M178','M178',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m178(path) -> None:
    Path(path).write_text(_render_m178())


f.render = _render_m178  # type: ignore[method-assign]
f.write = _write_m178    # type: ignore[method-assign]
