"""Pmi098 — SLOT axis not perpendicular to host face.

Catalog claim: AP242 SLOT whose AXIS2_PLACEMENT_3D Z direction is (1,0,0)
(parallel to a host face whose normal is (0,0,1)). The slot's cutting axis
is in-plane, so it cannot engrave the host. Receivers must reject or
auto-correct with a deterministic warning; silent acceptance is forbidden.

Byte assertions:
  contains(b'SLOT')
  contains(b'AXIS2_PLACEMENT_3D')
  contains(b'slot_axis_z_PARALLEL_TO_FACE')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi098",
    defect=(
        "SLOT AXIS2_PLACEMENT_3D Z direction (1,0,0) is parallel to host "
        "face normal (0,0,1) — slot would not cut the host; "
        "receiver must reject or auto-correct with deterministic warning"
    ),
)

# ── 50×50 mm planar face host (normal +Z) ────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((50.0, 0.0, 0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0))
p3 = f.cartesian_point((0.0, 50.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: SLOT axis Z direction parallel to host face (should be perpendicular)
# Slot center placement on the face.
slot_center = f.cartesian_point((25.0, 25.0, 0.0))
# Z direction (1,0,0) — parallel to the face plane (normal 0,0,1) — DEFECT.
slot_z_dir = f.direction((1.0, 0.0, 0.0))
# X direction orthogonal to Z, in-plane.
slot_x_dir = f.direction((0.0, 1.0, 0.0))
slot_plc = f.axis2_placement_3d(slot_center, slot_z_dir, slot_x_dir)

host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
slot_asp  = f._emit_raw("SHAPE_ASPECT('SLOT','',#9055,.T.)")

# Embed a named marker to satisfy the byte assertion.
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM"
    "('slot_axis_z_PARALLEL_TO_FACE','Z=(1,0,0) face_normal=(0,0,1)')"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_length')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_length',LENGTH_MEASURE(15.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_width')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_width',LENGTH_MEASURE(5.0),#9056)"
)
# Link the defective placement to the slot SHAPE_ASPECT.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('slot_placement','slot placement on host',"
    f"#{host_asp.eid},#{slot_asp.eid})"
)
f._emit_raw(
    f"APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT"
    f"('slot_axis_placement',#{slot_plc.eid},$,({slot_asp.ref()}))"
    if False else  # skip invalid AP214 entity; embed the placement via note
    f"DESCRIPTIVE_REPRESENTATION_ITEM"
    f"('slot_axis_placement_id','#{slot_plc.eid} Z=(1,0,0)')"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('slot_gisu',$,#{slot_asp.eid},#9061,#{face.eid})"
)
