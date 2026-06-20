"""Pmi020 — Saved view missing required mapped_item.

Catalog claim: For Saved Views, the draughting_model.items list must include a
mapped_item linking to the underlying draughting model. Files lacking it are
interpreted as "all PMI visible" by the SFA validator.

Reproducer recipe: draughting_model for a saved view containing only
annotation_occurrences, no mapped_item.

Byte assertions:
  count_entity_def(b'DRAUGHTING_MODEL') == 2
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  count_entity_def(b'MAPPED_ITEM') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi020",
    defect=(
        "saved-view DRAUGHTING_MODEL lacks required MAPPED_ITEM; "
        "SFA validator interprets missing mapped_item as 'all PMI visible'; "
        "receivers must warn and coerce all PMI to visible; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9060=geom_ctx

pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Base draughting_model (all PMI, no view filter) ───────────────────────────
pt_a = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
pt_b = f._emit_raw("CARTESIAN_POINT('',(20.0,0.0,0.0))")
pt_c = f._emit_raw("CARTESIAN_POINT('',(20.0,10.0,0.0))")
polyline = f._emit_raw(
    f"POLYLINE('dim_box',(#{pt_a.eid},#{pt_b.eid},#{pt_c.eid},#{pt_a.eid}))"
)
aco = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_occ',(#{pres_style.eid}),#{polyline.eid})"
)
base_dm = f._emit_raw(
    f"DRAUGHTING_MODEL('all_pmi',(#{aco.eid}),#9060)"
)

# ── Saved-view draughting_model — defect: no MAPPED_ITEM in items list ─────────
# A conforming saved-view DRAUGHTING_MODEL must include a MAPPED_ITEM that
# references the base draughting model; its absence means the view filter is
# undefined and the SFA validator falls back to "show all PMI".
# Intentionally omit MAPPED_ITEM here — that is the defect.
pt_d = f._emit_raw("CARTESIAN_POINT('',(5.0,0.0,0.0))")
pt_e = f._emit_raw("CARTESIAN_POINT('',(15.0,0.0,0.0))")
polyline2 = f._emit_raw(
    f"POLYLINE('dim_box2',(#{pt_d.eid},#{pt_e.eid},#{pt_d.eid}))"
)
aco2 = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_occ2',(#{pres_style.eid}),#{polyline2.eid})"
)
# Saved view: items list contains only the annotation occurrence, no MAPPED_ITEM.
saved_view_dm = f._emit_raw(
    f"DRAUGHTING_MODEL('saved_view_1',(#{aco2.eid}),#9060)"
)
