"""M043 — Layer with empty/duplicate name colliding with another.

Catalog claim: Multiple PRESENTATION_LAYER_ASSIGNMENT entries with the same
name caused conflict; OCCT didn't differentiate them by visibility.

Reproducer recipe: STEP with two PRESENTATION_LAYER_ASSIGNMENT of identical
name but different visibility flags.

Byte assertions:
  count_entity_def(b'PRESENTATION_LAYER_ASSIGNMENT') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M043",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing two PRESENTATION_LAYER_ASSIGNMENT "
        "entities with identical names but different visibility flags; "
        "input: AP242 STEP file where two PRESENTATION_LAYER_ASSIGNMENT entries "
        "share the name 'layer_A' — one marked visible, one hidden; "
        "OCCT Mantis 0032049 (96049f2): OCCT did not differentiate layers by "
        "visibility, grouping both under the same name and losing the visibility "
        "distinction; "
        "kernel must group layers by (name, visibility) tuple and preserve "
        "independent visibility state for each; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: layer name collision, duplicate PRESENTATION_LAYER_ASSIGNMENT, "
        "layers not differentiated by visibility, layer with empty name"
    ),
)

# ── Reference geometry items for the layers ───────────────────────────────────
pt1 = f._emit_raw("CARTESIAN_POINT('item_pt1',(0.,0.,0.))")
pt2 = f._emit_raw("CARTESIAN_POINT('item_pt2',(1.,0.,0.))")
pt3 = f._emit_raw("CARTESIAN_POINT('item_pt3',(0.,1.,0.))")

# ── DRAUGHTING_CALLOUT used as target items in layers ─────────────────────────
# Both layers share the name 'layer_A' — the defect
# Byte assertion: count_entity_def(b'PRESENTATION_LAYER_ASSIGNMENT') >= 2
layer_visible = f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('layer_A','visible layer',(#{pt1.eid}))"
)
# Second assignment — same name, different visibility intent
layer_hidden = f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('layer_A','hidden layer',(#{pt2.eid}))"
)

# ── DRAUGHTING_MODEL referencing both layers ──────────────────────────────────
draughting_model = f._emit_raw(
    f"DRAUGHTING_MODEL('collision_model',(#{layer_visible.eid},#{layer_hidden.eid}))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('layer-name-collision-duplicate-pla',"
    f"(#{layer_visible.eid},#{layer_hidden.eid},#{draughting_model.eid},"
    f"#{pt1.eid},#{pt2.eid},#{pt3.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M043.stp")
