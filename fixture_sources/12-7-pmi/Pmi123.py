"""Pmi123 — PROFILE_FEATURE used for sweep with no path.

Catalog claim: AP242 profile_feature classified as 'sweep' operation requires
a sweep_path attribute. This fixture emits a SHAPE_ASPECT('profile_feature')
with descriptive property feature_op='sweep' but no sweep_path geometric entity.
Receivers must reject E_SWEEP_MISSING_PATH or downgrade to extrude with
W_SWEEP_PATH_MISSING.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi123",
    defect=(
        "profile_feature SHAPE_ASPECT with feature_op='sweep' but no sweep_path entity; "
        "path curve missing — receiver must reject or downgrade to extrude"
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

# DEFECT: feature_op='sweep' declared but no sweep_path entity present
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('feature_op','sweep')"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'sweep_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('sweep_depth',LENGTH_MEASURE(10.0),#9056)"
)
# No sweep_path shape aspect or geometry is emitted — this is the defect
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('profile_on_face','profile on host',"
    f"#{host_asp.eid},#{profile_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('profile_gisu',$,#{profile_asp.eid},#9061,#{face.eid})"
)
