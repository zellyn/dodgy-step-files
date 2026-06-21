"""Pmi136 — FILLET radius larger than adjacent face's smallest extent.

Catalog claim: AP242 fillet rolling-ball radius must be strictly less than
the smallest extent of every adjacent face. This fixture emits
SHAPE_ASPECT('fillet') with fillet_radius=40mm on a 30x30mm face.
The ball cannot fit — construction fails. Receivers must reject or clamp
with W_FILLET_DOES_NOT_FIT.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi136",
    defect=(
        "fillet SHAPE_ASPECT with fillet_radius=40mm on 30x30mm face; "
        "rolling-ball radius exceeds face smallest extent (30mm) — "
        "ball cannot fit; receiver must reject or clamp"
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

host_asp   = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
fillet_asp = f._emit_raw("SHAPE_ASPECT('fillet','',#9055,.T.)")

# DEFECT: fillet_radius=40mm > face_extent=30mm (rolling-ball doesn't fit)
f._emit_raw(f"DIMENSIONAL_SIZE(#{fillet_asp.eid},'fillet_radius')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('fillet_radius',LENGTH_MEASURE(40.0),#9056)"
)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('face_min_extent','30.0')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('fillet_on_face','fillet on host',"
    f"#{host_asp.eid},#{fillet_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('fillet_gisu',$,#{fillet_asp.eid},#9061,#{face.eid})"
)
