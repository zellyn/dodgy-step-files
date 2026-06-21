"""Pmi096 — SLOT blind depth exceeds host face thickness (through-slot in non-through context).

Catalog claim: SLOT with end_condition='blind' but slot_depth=8.0 mm on a
host face declared as 5 mm thick. The depth exceeds the host thickness,
contradicting 'blind'. Receivers must reject or auto-promote to 'through'
with a deterministic warning; silent acceptance is forbidden.

Byte assertions:
  contains(b'SLOT')
  contains(b'slot_depth')
  contains(b'host_thickness')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi096",
    defect=(
        "SLOT end_condition='blind' but slot_depth=8.0 mm on a host with "
        "host_thickness=5.0 mm — depth exceeds thickness; "
        "receiver must reject or promote to 'through' with warning"
    ),
)

# ── 60×40 mm planar face host ─────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((60.0, 0.0, 0.0))
p2 = f.cartesian_point((60.0, 40.0, 0.0))
p3 = f.cartesian_point((0.0, 40.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: blind SLOT deeper than host thickness ─────────────────────────────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
slot_asp  = f._emit_raw("SHAPE_ASPECT('SLOT','',#9055,.T.)")

f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_length')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_length',LENGTH_MEASURE(15.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_width')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_width',LENGTH_MEASURE(6.0),#9056)"
)
# slot_depth = 8.0 mm — exceeds host_thickness = 5.0 mm while end_condition='blind'
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_depth')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_depth',LENGTH_MEASURE(8.0),#9056)"
)
# host thickness context
f._emit_raw(
    f"DESCRIPTIVE_REPRESENTATION_ITEM('host_thickness','5.0 mm')"
)
# end_condition='blind' (the defect: should be 'through' given depth >= thickness)
f._emit_raw(
    f"DESCRIPTIVE_REPRESENTATION_ITEM('end_condition','blind')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('slot_on_face','slot on host',"
    f"#{host_asp.eid},#{slot_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('slot_gisu',$,#{slot_asp.eid},#9061,#{face.eid})"
)
