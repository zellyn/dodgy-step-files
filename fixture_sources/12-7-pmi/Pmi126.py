"""Pmi126 — LOCATING_FEATURE tolerance zone larger than the locator feature.

Catalog claim: AP242 locating_feature implicit invariant requires
tolerance_zone_magnitude <= locator_feature_size. This fixture emits
locator_size=5mm with tolerance_zone_magnitude=20mm — the zone is 4x the
locator, effectively unconstrained. Receivers must reject as malformed; never
silently swap the values.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi126",
    defect=(
        "locating_feature SHAPE_ASPECT with locator_size=5mm and "
        "tolerance_zone_magnitude=20mm; zone 4x larger than locator — "
        "magnitude inversion makes locator functionally unconstrained"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((30.0, 0.0, 0.0))
p2 = f.cartesian_point((30.0, 30.0, 0.0)); p3 = f.cartesian_point((0.0, 30.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
locator_asp = f._emit_raw("SHAPE_ASPECT('locating_feature','',#9055,.T.)")

# DEFECT: tolerance_zone_magnitude (20mm) >> locator_size (5mm)
f._emit_raw(f"DIMENSIONAL_SIZE(#{locator_asp.eid},'locator_size')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('locator_size',LENGTH_MEASURE(5.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{locator_asp.eid},'tolerance_zone_magnitude')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tolerance_zone_magnitude',LENGTH_MEASURE(20.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('locator_on_face','locator on host',"
    f"#{host_asp.eid},#{locator_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('locator_gisu',$,#{locator_asp.eid},#9061,#{face.eid})"
)
