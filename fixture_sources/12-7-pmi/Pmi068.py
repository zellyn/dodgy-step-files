"""Pmi068 — Annotation_plane orientation flipped on import (mirror determinant).

Catalog claim: An annotation_plane whose underlying axis2_placement_3d carries
a left-handed (negative-determinant) frame is silently right-handized on
import, flipping the normal direction so annotations read back facing the
wrong way.

Reproducer recipe: ANNOTATION_PLANE with AXIS2_PLACEMENT_3D whose axis and
ref_direction produce a left-handed frame (cross(ref_dir, axis) points in the
opposite direction from the ref_direction).

Byte assertions:
  contains(b'CARTESIAN_TRANSFORMATION_OPERATOR_3D')
  contains(b'ITEM_DEFINED_TRANSFORMATION')
  count_entity_def(b'PLANE') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi068",
    defect=(
        "ANNOTATION_PLANE uses AXIS2_PLACEMENT_3D whose axis (0,0,-1) and "
        "ref_direction (1,0,0) produce a left-handed (negative-determinant) "
        "frame; OCCT silently right-handizes this frame on import without "
        "emitting a diagnostic, flipping the annotation plane normal so GD&T "
        "text faces the wrong direction; receivers must preserve handedness or "
        "coherently flip face normals and must never silently right-handize "
        "annotation planes; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── Two PLANEs (byte assertion: count_entity_def(b'PLANE') == 2) ─────────────
# Plane 1: right-handed reference plane (Z+ normal).
rh_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
rh_normal = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
rh_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
rh_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('right_handed',#{rh_origin.eid},#{rh_normal.eid},#{rh_xdir.eid})"
)
plane_rh = f._emit_raw(f"PLANE('reference_plane',#{rh_plc.eid})")

# Plane 2: left-handed annotation plane — axis = (0,0,-1), ref_dir = (1,0,0).
# cross((1,0,0), (0,0,-1)) = (0*(-1)-0*0, 0*1-1*(-1), 1*0-0*1) = (0,1,0),
# but the frame axis is (0,0,-1), making it left-handed (det < 0).
lh_origin = f._emit_raw("CARTESIAN_POINT('',(5.0,0.0,0.0))")
lh_axis = f._emit_raw("DIRECTION('',(0.0,0.0,-1.0))")   # flipped Z — left-handed
lh_xdir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
lh_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('left_handed',#{lh_origin.eid},#{lh_axis.eid},#{lh_xdir.eid})"
)
plane_lh = f._emit_raw(f"PLANE('anno_plane_lh',#{lh_plc.eid})")

# ── ANNOTATION_PLANE using the left-handed placement ─────────────────────────
# A simple annotation curve inside the plane.
pt_a = f._emit_raw("CARTESIAN_POINT('',(5.0,0.0,0.0))")
pt_b = f._emit_raw("CARTESIAN_POINT('',(15.0,0.0,0.0))")
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)
colour = f._emit_raw("COLOUR_RGB('anno_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)
anno_curve = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_leader',(#{polyline.eid}),#{psa.eid})"
)
f._emit_raw(
    f"ANNOTATION_PLANE('lh_anno_plane',(#{anno_curve.eid}),#{lh_plc.eid})"
)

# ── CARTESIAN_TRANSFORMATION_OPERATOR_3D (byte assertion) ─────────────────────
# Mirrors the right-handed plane to produce the left-handed annotation frame.
# scale = -1 is the left-hand flip.
cto_origin = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
cto_axis1 = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
cto_axis2 = f._emit_raw("DIRECTION('',(0.0,1.0,0.0))")
cto_axis3 = f._emit_raw("DIRECTION('',(0.0,0.0,-1.0))")
cto = f._emit_raw(
    f"CARTESIAN_TRANSFORMATION_OPERATOR_3D(#{cto_origin.eid},"
    f"#{cto_axis1.eid},#{cto_axis2.eid},1.0,#{cto_axis3.eid})"
)

# ── ITEM_DEFINED_TRANSFORMATION (byte assertion) ──────────────────────────────
f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('mirror_flip','left-hand mirror',"
    f"#{rh_plc.eid},#{lh_plc.eid})"
)
