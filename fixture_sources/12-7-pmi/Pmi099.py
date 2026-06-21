"""Pmi099 — Three coaxial SLOT features instead of a RECTANGULAR_PATTERN.

Catalog claim: Three independent SLOT SHAPE_ASPECTs sharing the same
dimensions (length=15, width=5, depth=2), evenly spaced 25 mm apart along X,
with no RECTANGULAR_PATTERN linking them. The parametric pattern relationship
is lost; receivers must emit W_FEATURE_PATTERN_LOST when observing this form.

Byte assertions:
  count_entity_def(b'SHAPE_ASPECT') >= 3
  contains(b'SLOT')
  not_contains(b'RECTANGULAR_PATTERN')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi099",
    defect=(
        "three independent SLOT SHAPE_ASPECTs sharing same dimensions and spacing "
        "with no pattern entity linking them — parametric pattern relationship "
        "lost; receiver should emit W_FEATURE_PATTERN_LOST diagnostic"
    ),
)

# ── 80×50 mm planar face host ─────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((80.0, 0.0, 0.0))
p2 = f.cartesian_point((80.0, 50.0, 0.0))
p3 = f.cartesian_point((0.0, 50.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# ── DEFECT: Three independent SLOT SHAPe_ASPECTs, no RECTANGULAR_PATTERN ─────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")

for i, cx in enumerate([15.0, 40.0, 65.0], start=1):
    slot_asp = f._emit_raw(
        f"SHAPE_ASPECT('SLOT','slot_{i}',#9055,.T.)"
    )
    f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_length')")
    f._emit_raw(
        f"MEASURE_REPRESENTATION_ITEM('slot_length_{i}',LENGTH_MEASURE(15.0),#9056)"
    )
    f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_width')")
    f._emit_raw(
        f"MEASURE_REPRESENTATION_ITEM('slot_width_{i}',LENGTH_MEASURE(5.0),#9056)"
    )
    f._emit_raw(f"DIMENSIONAL_SIZE(#{slot_asp.eid},'slot_depth')")
    f._emit_raw(
        f"MEASURE_REPRESENTATION_ITEM('slot_depth_{i}',LENGTH_MEASURE(2.0),#9056)"
    )
    f._emit_raw(
        f"SHAPE_ASPECT_RELATIONSHIP('slot_{i}_on_face','slot {i} on host',"
        f"#{host_asp.eid},#{slot_asp.eid})"
    )
    f._emit_raw(
        f"GEOMETRIC_ITEM_SPECIFIC_USAGE('slot_{i}_gisu',$,#{slot_asp.eid},#9061,#{face.eid})"
    )
