"""Pmi118 — FLAT_PATTERN bend axis not parallel to bend line.

Catalog claim: AP242 flat_pattern bend rotation axis must be parallel to the
bend line direction. This fixture emits a bend_line along Y=(0,1,0) with a
rotation axis along X=(1,0,0) — orthogonal, not parallel. Receivers must
reject or project with W_BEND_AXIS_PROJECTED.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi118",
    defect=(
        "flat_pattern bend_line direction Y=(0,1,0) contradicts rotation "
        "axis X=(1,0,0) — bend axis orthogonal to bend line; "
        "receiver must reject or project axis onto line with W_BEND_AXIS_PROJECTED"
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
pattern_asp = f._emit_raw("SHAPE_ASPECT('flat_pattern','',#9055,.T.)")
bend_asp    = f._emit_raw("SHAPE_ASPECT('bend_line','',#9055,.T.)")

# bend_line direction: along Y = (0,1,0)
bend_line_pt  = f.cartesian_point((25.0, 0.0, 0.0))
bend_line_dir = f.direction((0.0, 1.0, 0.0))
bend_line_vec = f.vector(bend_line_dir, 50.0)
bend_line_geom = f.line(bend_line_pt, bend_line_vec)

# rotation axis: along X = (1,0,0) — ORTHOGONAL to bend_line (defect)
bend_axis_loc = f.cartesian_point((25.0, 25.0, 0.0))
bend_axis_dir = f.direction((1.0, 0.0, 0.0))  # NOT parallel to (0,1,0)
bend_axis_plc = f._emit_raw(
    f"AXIS1_PLACEMENT('bend_rotation_axis',#{bend_axis_loc.eid},#{bend_axis_dir.eid})"
)

f._emit_raw(f"DIMENSIONAL_SIZE(#{bend_asp.eid},'bend_angle')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('bend_angle',PLANE_ANGLE_MEASURE(1.5708),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'material_thickness')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('material_thickness',LENGTH_MEASURE(2.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_has_bend','flat pattern has bend',"
    f"#{pattern_asp.eid},#{bend_asp.eid})"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_on_face','flat pattern on host',"
    f"#{host_asp.eid},#{pattern_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('fp_gisu',$,#{pattern_asp.eid},#9061,#{face.eid})"
)
