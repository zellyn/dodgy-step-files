"""M184 — AP238 executable_relationship forms a cycle (A precedes B, B precedes A)

Catalog claim: Two EXECUTABLE_RELATIONSHIP entities form a cycle where
operation A precedes operation B and operation B precedes operation A.
The workplan has no valid topological order; consumers either deadlock
during scheduling or pick an arbitrary order that breaks the dependency.

Reproducer recipe: two MACHINING_OPERATIONs #100 and #101; two
EXECUTABLE_RELATIONSHIPs (#100->>#101) and (#101->>#100) declared
in the same file.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  count_entity_def(b'EXECUTABLE_RELATIONSHIP') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M184",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where EXECUTABLE_RELATIONSHIP entities "
        "form a cycle: operation A precedes B and B precedes A simultaneously; "
        "input: AP238 STEP-NC file containing a WORKPLAN with two MACHINING_OPERATION entities; "
        "MACHINING_OPERATION 'drill_op_A' (#200) and 'drill_op_B' (#201) are declared; "
        "EXECUTABLE_RELATIONSHIP 'A_precedes_B' (#210) declares #200 (A) must precede #201 (B); "
        "EXECUTABLE_RELATIONSHIP 'B_precedes_A' (#211) declares #201 (B) must precede #200 (A); "
        "these two relationships form a cycle: A->B and B->A simultaneously; "
        "the workplan has no valid topological order — no starting point exists; "
        "consumers either deadlock during scheduling or pick an arbitrary order breaking dependencies; "
        "per ISO 10303-238 §6.4 executable_relationship acyclicity invariant: "
        "the executable-relationship graph must be acyclic for a valid schedule; "
        "kernel must detect cycles in the executable-relationship graph and reject as unschedulable; "
        "synonyms: AP238 dependency cycle, STEP-NC workplan won't schedule, "
        "executable graph has loop, AP238 executable_relationship cycle, "
        "STEP-NC dependency graph cyclic, workplan deadlock from circular precedes, "
        "AP238 dependency cycle, STEP-NC executable graph loop, "
        "workplan A precedes B precedes A, circular precedes"
    ),
    schema="AP242",
)


def _render_m184() -> str:
    """Render AP238 STEP-NC file with EXECUTABLE_RELATIONSHIP cycle: A->B and B->A.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #200      MACHINING_DRILLING_OPERATION 'drill_op_A' — first operation
      #201      MACHINING_DRILLING_OPERATION 'drill_op_B' — second operation
      #210      EXECUTABLE_RELATIONSHIP 'A_precedes_B' — A must precede B
      #211      EXECUTABLE_RELATIONSHIP 'B_precedes_A' — DEFECT: B must precede A (cycle!)
      #50       WORKPLAN 'cyclic_dependency_program' — references both ops
      #51       MACHINING_WORKINGSTEP 'drill_step_A'
      #52       MACHINING_WORKINGSTEP 'drill_step_B'
      #60       WORKPIECE 'drill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M184: AP238 executable_relationship forms a cycle (A precedes B, B precedes A) */")
    lines.append("/* DEFECT: EXECUTABLE_RELATIONSHIP A->B and B->A create a dependency cycle */")
    lines.append("/* Workplan has no valid topological order — no valid starting operation exists */")
    lines.append("/* Consumer scheduler either deadlocks or picks arbitrary order breaking dependencies */")
    lines.append("/* Per ISO 10303-238 §6.4 executable-relationship graph must be acyclic */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: count_entity_def(b'EXECUTABLE_RELATIONSHIP') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M184: AP238 executable_relationship cycle A precedes B precedes A'),'2;1');")
    lines.append("FILE_NAME('M184.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-executable-relationship-dependency-cycle',")
    lines.append("  (#210,#211,#60));")
    lines.append("/* WORKPIECE 'drill_workpiece' for both drilling operations */")
    lines.append("#60=WORKPIECE('drill_workpiece','Workpiece for cyclic dependency test',$,$,$,$,$);")
    lines.append("/* Operation A: drill_op_A — first drilling operation */")
    lines.append("#200=DRILLING_OPERATION('drill_op_A',$,$,$,$,$,$,$,$,$,$,$,$);")
    lines.append("/* Operation B: drill_op_B — second drilling operation */")
    lines.append("#201=DRILLING_OPERATION('drill_op_B',$,$,$,$,$,$,$,$,$,$,$,$);")
    lines.append("/* Byte assertion: count_entity_def(b'EXECUTABLE_RELATIONSHIP') >= 2 */")
    lines.append("/* EXECUTABLE_RELATIONSHIP 'A_precedes_B': A (#200) must execute before B (#201) */")
    lines.append("#210=EXECUTABLE_RELATIONSHIP('A_precedes_B','A must precede B',#200,#201);")
    lines.append("/* DEFECT: 'B_precedes_A': B (#201) must execute before A (#200) — CYCLE! */")
    lines.append("#211=EXECUTABLE_RELATIONSHIP('B_precedes_A','B must precede A',#201,#200);")
    lines.append("/* MACHINING_WORKINGSTEP links each op to the shared workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('drill_step_A','Drill step A',#200,#60,$);")
    lines.append("#52=MACHINING_WORKINGSTEP('drill_step_B','Drill step B',#201,#60,$);")
    lines.append("/* WORKPLAN: both steps with circular dependency — no valid schedule */")
    lines.append("#50=WORKPLAN('cyclic_dependency_program','Cyclic dependency workplan',(),$,(#51,#52));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M184','M184','M184',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m184(path) -> None:
    Path(path).write_text(_render_m184())


f.render = _render_m184  # type: ignore[method-assign]
f.write = _write_m184    # type: ignore[method-assign]
