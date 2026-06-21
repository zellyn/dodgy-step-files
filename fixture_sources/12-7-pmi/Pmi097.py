"""Pmi097 — SLOT end-condition declared 'round_end' but profile is rectangular.

Catalog claim: AP242 SLOT with end_condition='round_end' and
profile_shape='rectangular' — the end-condition string contradicts the
profile geometry. Receivers must reject as inconsistent and name the
contradicting attributes; never silently pick one side.

Byte assertions:
  contains(b'SLOT')
  contains(b'round_end')
  contains(b'rectangular')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi097",
    defect=(
        "SLOT end_condition='round_end' contradicts profile_shape='rectangular'; "
        "receiver must reject as inconsistent and name the violated attribute"
    ),
)

# ── 50×50 mm planar face host ─────────────────────────────────────────────────
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

# ── DEFECT: SLOT end_condition contradicts profile_shape ─────────────────────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
slot_asp  = f._emit_raw("SHAPE_ASPECT('SLOT','',#9055,.T.)")

f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_length')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_length',LENGTH_MEASURE(20.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_width')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_width',LENGTH_MEASURE(6.0),#9056)"
)
# end_condition='round_end' — requires semicircular ends in profile
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('end_condition','round_end')"
)
# profile_shape='rectangular' — four sharp corners: CONTRADICTS round_end
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('profile_shape','rectangular')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('slot_on_face','slot on host',"
    f"#{host_asp.eid},#{slot_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('slot_gisu',$,#{slot_asp.eid},#9061,#{face.eid})"
)
