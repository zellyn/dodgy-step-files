"""Pmi019 — camera_model_d3 viewpoint not modeled per RP §9.

Catalog claim: camera_model_d3 lacks the orthonormal/orientation conventions
expected by RP §9 (e.g., view direction not orthogonal to up direction).

Reproducer recipe: camera_model_d3 with view-up parallel to view-direction.

Byte assertions:
  contains(b'CAMERA_MODEL_D3')
  contains(b'VIEW_VOLUME')
  contains(b'ANNOTATION_PLANE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi019",
    defect=(
        "CAMERA_MODEL_D3 with view-up direction (0,0,1) parallel to view-direction (0,0,1); "
        "violates RP §9 orthonormality requirement; gmsh crashes with signal(11); "
        "receivers must warn or orthonormalise via Gram-Schmidt, never crash; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9060=geom_ctx

pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Annotation plane (required by byte assertion) ─────────────────────────────
ap_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
ap_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
ap_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
ap_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{ap_origin.eid},#{ap_normal.eid},#{ap_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('ann_plane',#{ap_plc.eid})")
ann_plane = f._emit_raw(
    f"ANNOTATION_PLANE('view_plane',(#{pres_style.eid}),#{plane.eid})"
)

# ── CAMERA_MODEL_D3: defect — view-up parallel to view-direction ──────────────
# view-direction = (0,0,1); view-up = (0,0,1) — same vector, not orthogonal.
# RP §9 requires view_up ⊥ view_plane_normal; a parallel pair is degenerate.
cam_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,100.0))")
# AXIS2_PLACEMENT_3D: origin, axis (view direction), ref_direction (view up)
# Defect: both axis and ref_direction point along Z — not orthogonal.
view_dir = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
view_up = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
cam_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{cam_origin.eid},#{view_dir.eid},#{view_up.eid})"
)

# VIEW_VOLUME: parallel projection; signature is
# VIEW_VOLUME('', #planar_extent, .PARALLEL., front_plane, .F., left_plane, right_plane, back_plane)
proj_extent = f._emit_raw("PLANAR_EXTENT('',200.0,150.0)")
prj_vol = f._emit_raw(
    f"VIEW_VOLUME('',#{proj_extent.eid},.PARALLEL.,0.0,.F.,0.0,1.0,200.0)"
)

# CAMERA_MODEL_D3 ties the placement to the view volume.
cam = f._emit_raw(
    f"CAMERA_MODEL_D3('bad_camera',#{cam_plc.eid},#{prj_vol.eid})"
)

# Draughting model referencing both the annotation plane and the bad camera.
f._emit_raw(
    f"DRAUGHTING_MODEL('pmi_view',(#{ann_plane.eid},#{cam.eid}),#9060)"
)
