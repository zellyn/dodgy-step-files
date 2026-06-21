"""Pmi134 — CHAMFER with two contradictory chamfer_angle attributes (45 and 60 deg).

Catalog claim: AP242 chamfer carries exactly one chamfer_angle. This fixture
emits two DIMENSIONAL_SIZE records both named 'chamfer_angle': one with
PLANE_ANGLE_MEASURE(0.7854) (45°) and one with PLANE_ANGLE_MEASURE(1.0472) (60°).
Receivers must reject as malformed; never silently pick one angle.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi134",
    defect=(
        "chamfer SHAPE_ASPECT with two contradictory chamfer_angle attributes: "
        "0.7854rad (45deg) and 1.0472rad (60deg); duplicate attribute conflict — "
        "receiver must reject"
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
chamfer_asp = f._emit_raw("SHAPE_ASPECT('chamfer','',#9055,.T.)")

# DEFECT: two chamfer_angle DIMENSIONAL_SIZE records with conflicting values
f._emit_raw(f"DIMENSIONAL_SIZE(#{chamfer_asp.eid},'chamfer_angle')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('chamfer_angle_45',PLANE_ANGLE_MEASURE(0.7853981634),#9057)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{chamfer_asp.eid},'chamfer_angle')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('chamfer_angle_60',PLANE_ANGLE_MEASURE(1.0471975512),#9057)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{chamfer_asp.eid},'chamfer_size')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('chamfer_size',LENGTH_MEASURE(5.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('chamfer_on_face','chamfer on host',"
    f"#{host_asp.eid},#{chamfer_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('chamfer_gisu',$,#{chamfer_asp.eid},#9061,#{face.eid})"
)
