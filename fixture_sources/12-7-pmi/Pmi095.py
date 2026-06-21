"""Pmi095 — SLOT feature with length less than width (degenerate slot).

Catalog claim: AP242 SLOT geometric invariant requires slot_length >= slot_width.
This fixture emits slot_length=8.0 mm and slot_width=20.0 mm (length < width).
Receivers must reject or reclassify; never silently swap values.

Byte assertions:
  contains(b'SLOT')
  contains(b'slot_length')
  contains(b'slot_width')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi095",
    defect=(
        "SLOT SHAPE_ASPECT with slot_length=8.0 mm and slot_width=20.0 mm; "
        "length < width violates the SLOT class invariant; "
        "receiver must reject or reclassify as rectangular pocket with warning"
    ),
)

# ── 50×50 mm planar face (host) ───────────────────────────────────────────────
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

# ── DEFECT: SLOT with slot_length < slot_width ────────────────────────────────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
slot_asp  = f._emit_raw("SHAPE_ASPECT('SLOT','',#9055,.T.)")

# slot_length = 8.0 mm (SHORTER than width — defect)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_length')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_length',LENGTH_MEASURE(8.0),#9056)"
)
# slot_width = 20.0 mm (wider than length — defect)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_width')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_width',LENGTH_MEASURE(20.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_depth')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('slot_depth',LENGTH_MEASURE(3.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('slot_on_face','slot on host',"
    f"#{host_asp.eid},#{slot_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('slot_gisu',$,#{slot_asp.eid},#9061,#{face.eid})"
)
