"""Pmi122 — PROFILE_FEATURE with conflicting profile + draft angles (negative draft).

Catalog claim: AP242 profile_feature with small profile (half-extent 2.5 mm),
sweep_depth=10mm, and draft_angle=-45° (-0.7854 rad). The taper magnitude
tan(45°)×10=10mm far exceeds the 2.5mm half-extent, producing a self-intersecting
taper. Receivers must reject E_DRAFT_EXCEEDS_PROFILE or clamp with W_DRAFT_CLAMPED.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi122",
    defect=(
        "profile_feature sweep_depth=10mm profile_half_extent=2.5mm draft_angle=-0.7854rad; "
        "negative draft taper of tan(45deg)*10=10mm exceeds half-extent 2.5mm — "
        "self-intersecting taper; receiver must reject or clamp"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((50.0, 0.0, 0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0)); p3 = f.cartesian_point((0.0, 50.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
profile_asp = f._emit_raw("SHAPE_ASPECT('profile_feature','',#9055,.T.)")

# DEFECT: negative draft angle -45 deg, depth 10mm, half_extent 2.5mm
# tan(45deg) * 10mm = 10mm >> 2.5mm half_extent -> self-intersecting taper
f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'sweep_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('sweep_depth',LENGTH_MEASURE(10.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'profile_half_extent')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('profile_half_extent',LENGTH_MEASURE(2.5),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'draft_angle')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('draft_angle',PLANE_ANGLE_MEASURE(-0.7854),#9057)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('profile_on_face','profile on host',"
    f"#{host_asp.eid},#{profile_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('profile_gisu',$,#{profile_asp.eid},#9061,#{face.eid})"
)
