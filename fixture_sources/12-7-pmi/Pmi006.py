"""Pmi006 — Saved-view name location ambiguous (camera_model_d3 vs model_geometric_view).

Catalog claim: Older guidance put the Saved-View name on CAMERA_MODEL_D3.name.
AP242 Ed.2+ recommends MODEL_GEOMETRIC_VIEW.name. Files omitting the name from
MODEL_GEOMETRIC_VIEW are read as anonymous by Ed.2-only readers.

Reproducer: two CAMERA_MODEL_D3 instances both named 'Front', two
DRAUGHTING_MODELs — no MODEL_GEOMETRIC_VIEW carrying the canonical name.

Byte assertions:
  count_entity_def(b'CAMERA_MODEL_D3') == 2
  count_entity_def(b'DRAUGHTING_MODEL') == 2
  count_entity_def(b'MODEL_GEOMETRIC_VIEW') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi006",
    defect=(
        "saved-view name on CAMERA_MODEL_D3 only; no MODEL_GEOMETRIC_VIEW; "
        "two CAMERA_MODEL_D3('Front') + two DRAUGHTING_MODELs; "
        "Ed.2-only readers see anonymous views; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9060=geom_ctx

# ── Shared view direction components ─────────────────────────────────────────
# Camera 1: front view — looking along -Y.
view_dir1 = f._emit_raw("DIRECTION('',(0.0,-1.0,0.0))")
up_dir1 = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
view_pt1 = f._emit_raw("CARTESIAN_POINT('',(0.0,100.0,0.0))")
view_plc1 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{view_pt1.eid},#{view_dir1.eid},#{up_dir1.eid})"
)
# VIEW_VOLUME for the camera.
proj1 = f._emit_raw("PLANAR_EXTENT('',200.0,150.0)")
vol1 = f._emit_raw(
    f"VIEW_VOLUME('',#{proj1.eid},.PARALLEL.,0.0,.F.,0.0,1.0,200.0)"
)

# Defect: saved-view name placed on CAMERA_MODEL_D3, not MODEL_GEOMETRIC_VIEW.
cam1 = f._emit_raw(
    f"CAMERA_MODEL_D3('Front',#{view_plc1.eid},#{vol1.eid})"
)

# Camera 2: a second 'Front' view (duplicate name as sometimes produced by
# CATIA-style writers that don't deduplicate view names).
view_dir2 = f._emit_raw("DIRECTION('',(0.0,-1.0,0.0))")
up_dir2 = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
view_pt2 = f._emit_raw("CARTESIAN_POINT('',(0.0,200.0,0.0))")
view_plc2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{view_pt2.eid},#{view_dir2.eid},#{up_dir2.eid})"
)
proj2 = f._emit_raw("PLANAR_EXTENT('',200.0,150.0)")
vol2 = f._emit_raw(
    f"VIEW_VOLUME('',#{proj2.eid},.PARALLEL.,0.0,.F.,0.0,1.0,200.0)"
)
cam2 = f._emit_raw(
    f"CAMERA_MODEL_D3('Front',#{view_plc2.eid},#{vol2.eid})"
)

# Two DRAUGHTING_MODELs, one per camera — no MODEL_GEOMETRIC_VIEW.
f._emit_raw(f"DRAUGHTING_MODEL('SavedView1',(#{cam1.eid}),#9060)")
f._emit_raw(f"DRAUGHTING_MODEL('SavedView2',(#{cam2.eid}),#9060)")
# Intentionally no MODEL_GEOMETRIC_VIEW — that is the defect.
