"""M044 — Empty DRAUGHTING_MODEL / PRESENTATION_LAYER_ASSIGNMENT.

Catalog claim: STEP file with empty presentation entities (no assigned items)
caused reader exception in OCCT.

Reproducer recipe: PRESENTATION_LAYER_ASSIGNMENT('layer1','',(),(..)) with
empty items list.

Byte assertions:
  contains(b'PRESENTATION_LAYER_ASSIGNMENT')
  contains(b'DRAUGHTING_MODEL')
  matches(rb'PRESENTATION_LAYER_ASSIGNMENT\\([^)]*,\\(\\)\\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M044",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing PRESENTATION_LAYER_ASSIGNMENT with empty "
        "items list and a DRAUGHTING_MODEL referencing it; "
        "input: AP242 STEP file where PRESENTATION_LAYER_ASSIGNMENT has an empty "
        "assigned-items aggregate () — no geometry is referenced; "
        "OCCT Mantis 0030870 (9063f1e): reader threw an exception when iterating "
        "over an empty items list in presentation entity; "
        "kernel must tolerate empty PRESENTATION_LAYER_ASSIGNMENT and "
        "DRAUGHTING_MODEL (emit empty layer, do not crash); "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: empty DRAUGHTING_MODEL crash, presentation entity has no items, "
        "reader exception on empty layer assignment, PRESENTATION_LAYER_ASSIGNMENT empty"
    ),
)

# ── PRESENTATION_LAYER_ASSIGNMENT with empty items list — the defect ──────────
# Byte assertion: contains(b'PRESENTATION_LAYER_ASSIGNMENT')
# Byte assertion: matches(rb'PRESENTATION_LAYER_ASSIGNMENT\([^)]*,\(\)\)')
pla_empty = f._emit_raw(
    "PRESENTATION_LAYER_ASSIGNMENT('layer1','',())"
)

# A second PLA also empty to confirm the pattern survives multiple instances
pla_empty2 = f._emit_raw(
    "PRESENTATION_LAYER_ASSIGNMENT('layer2','backup layer',())"
)

# ── DRAUGHTING_MODEL referencing both empty layers ────────────────────────────
# Byte assertion: contains(b'DRAUGHTING_MODEL')
draughting_model = f._emit_raw(
    f"DRAUGHTING_MODEL('empty_model',(#{pla_empty.eid},#{pla_empty2.eid}))"
)

# ── A minimal geometry point so the file has at least one geometric entity ────
anchor_pt = f._emit_raw("CARTESIAN_POINT('anchor',(0.,0.,0.))")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('empty-draughting-model-pla',"
    f"(#{pla_empty.eid},#{pla_empty2.eid},#{draughting_model.eid},"
    f"#{anchor_pt.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M044.stp")
