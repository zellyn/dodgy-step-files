"""Pmi121 — PROFILE_FEATURE depth direction not perpendicular to profile plane.

Catalog claim: AP242 profile_feature straight extrude requires sweep direction
perpendicular to the profile plane. This fixture emits a profile on the XY
plane (normal +Z) with sweep direction (1,0,0) — parallel to the profile plane,
producing zero swept volume. Receivers must reject E_DEGENERATE_EXTRUDE_DIRECTION
or project with W_EXTRUDE_DIR_PROJECTED.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi121",
    defect=(
        "profile_feature profile plane normal=(0,0,1) but sweep direction=(1,0,0) "
        "lies in the profile plane — degenerate extrude produces zero volume; "
        "depth_dir_vs_normal documents the parallelism"
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

# Profile plane normal: +Z = (0,0,1)
# Sweep direction: +X = (1,0,0) — IN the profile plane, not perpendicular (defect)
sweep_dir = f.direction((1.0, 0.0, 0.0))  # parallel to profile XY plane

f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'sweep_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('sweep_depth',LENGTH_MEASURE(10.0),#9056)"
)
# Marker documenting the direction defect
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM"
    "('depth_dir_vs_normal','sweep_dir=(1,0,0) profile_normal=(0,0,1) DOT=0 PARALLEL')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('profile_on_face','profile on host',"
    f"#{host_asp.eid},#{profile_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('profile_gisu',$,#{profile_asp.eid},#9061,#{face.eid})"
)
