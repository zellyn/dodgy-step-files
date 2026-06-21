"""Pmi114 — FLAT_PATTERN bend-angle exceeding 180°.

Catalog claim: AP242 flat_pattern bend_angle must be in (0, π) radians.
This fixture emits bend_angle=4.7124 rad (270°) — geometrically impossible
(would fold sheet through itself). Receivers must reject E_BEND_ANGLE_OUT_OF_RANGE
or clamp to 180° deterministically.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi114",
    defect=(
        "flat_pattern SHAPE_ASPECT with child bend_line whose bend_angle="
        "PLANE_ANGLE_MEASURE(4.7124 rad)=270°; angle > 180° is physically "
        "impossible (sheet self-intersects)"
    ),
)

# 50x50 mm planar face
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

# DEFECT: flat_pattern with bend_angle > 180°
host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
pattern_asp = f._emit_raw("SHAPE_ASPECT('flat_pattern','',#9055,.T.)")
bend_asp    = f._emit_raw("SHAPE_ASPECT('bend_line','',#9055,.T.)")

# bend_angle = 4.7124 rad = 270° (> 180°, physically impossible)
f._emit_raw(f"DIMENSIONAL_SIZE(#{bend_asp.eid},'bend_angle')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('bend_angle',PLANE_ANGLE_MEASURE(4.7124),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_has_bend','flat pattern has bend line',"
    f"#{pattern_asp.eid},#{bend_asp.eid})"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_on_face','flat pattern on host',"
    f"#{host_asp.eid},#{pattern_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('fp_gisu',$,#{pattern_asp.eid},#9061,#{face.eid})"
)
