"""Pmi101 — GROOVE sweep does not close (open path on cylindrical host).

Catalog claim: AP242 circumferential GROOVE sweep_end_angle must equal
sweep_start_angle + 2π. This fixture emits sweep_start_angle=0.0 and
sweep_end_angle=4.8869 rad (~280° — not 2π). Receivers must reject or
reclassify as partial-arc slot; silent acceptance is forbidden.

Byte assertions:
  contains(b'GROOVE')
  contains(b'sweep_end')
  contains(b'sweep_end_OPEN')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi101",
    defect=(
        "GROOVE sweep_start_angle=0.0 and sweep_end_angle=4.8869 rad (~280°); "
        "groove sweep does not close (should be 2π=6.2832 rad); "
        "receiver must reject or reclassify as partial-arc slot"
    ),
)

# ── 50×50 mm planar face host ─────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0,  0.0,  0.0))
p1 = f.cartesian_point((50.0, 0.0,  0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0))
p3 = f.cartesian_point((0.0,  50.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: GROOVE sweep does not close ───────────────────────────────────────
host_asp   = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
groove_asp = f._emit_raw("SHAPE_ASPECT('GROOVE','',#9055,.T.)")

f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'groove_width')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('groove_width',LENGTH_MEASURE(3.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'groove_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('groove_depth',LENGTH_MEASURE(2.0),#9056)"
)
# sweep_start_angle = 0.0 rad
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('sweep_start','0.0 rad')"
)
# sweep_end_angle = 4.8869 rad (~280°) — does NOT close (should be 2π)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('sweep_end_OPEN','4.8869 rad (approx 280 deg)')"
)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('sweep_end','4.8869')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('groove_on_face','groove on host',"
    f"#{host_asp.eid},#{groove_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('groove_gisu',$,#{groove_asp.eid},#9061,#{face.eid})"
)
