"""Pmi015 — Annotation geometry must be in plane PARALLEL to annotation_plane (small offset).

Catalog claim: CAD systems offset annotation geometry slightly above the
underlying annotation_plane. RP says elements must lie in a plane parallel to
the annotation_plane, not necessarily on it. Strict-on-plane checks reject
valid files.

Reproducer recipe: annotation_plane at z=0; polyline points all at z=0.05.

Byte assertions:
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'ANNOTATION_PLANE')
  contains(b'POLYLINE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi015",
    defect=(
        "ANNOTATION_PLANE at z=0; polyline annotation geometry at z=0.05 "
        "(parallel offset); strict on-plane checks reject this valid file; "
        "the defect is a presentation/PMI property the shape-count oracles cannot observe, and here it also sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9060=geom_ctx

# Presentation style.
pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── annotation_plane at z=0 ───────────────────────────────────────────────────
ap_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
ap_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
ap_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
ap_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{ap_origin.eid},#{ap_normal.eid},#{ap_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('ann_plane_z0',#{ap_plc.eid})")
ann_plane = f._emit_raw(
    f"ANNOTATION_PLANE('ann_plane',(#{pres_style.eid}),#{plane.eid})"
)

# ── Annotation geometry: polyline at z=0.05 (parallel but offset) ─────────────
# Defect: all points are at z=0.05, which is parallel to but not on the
# annotation_plane at z=0. Strict receivers reject this; correct behavior is
# to accept geometry in any plane parallel to the annotation_plane within
# representation_context tolerance.
pt1 = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.05))")
pt2 = f._emit_raw("CARTESIAN_POINT('',(10.0,0.0,0.05))")
pt3 = f._emit_raw("CARTESIAN_POINT('',(10.0,5.0,0.05))")
pt4 = f._emit_raw("CARTESIAN_POINT('',(0.0,5.0,0.05))")
polyline = f._emit_raw(
    f"POLYLINE('dim_box',(#{pt1.eid},#{pt2.eid},#{pt3.eid},#{pt4.eid},#{pt1.eid}))"
)
curve_occ = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_occ',(#{pres_style.eid}),#{polyline.eid})"
)

# Draughting model linking the annotation_plane and the offset annotation.
f._emit_raw(
    f"DRAUGHTING_MODEL('pmi_view',(#{ann_plane.eid},#{curve_occ.eid}),#9060)"
)
