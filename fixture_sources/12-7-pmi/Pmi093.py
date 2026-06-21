"""Pmi093 — RECTANGULAR_PATTERN with zero spacing in one direction.

Catalog claim: AP242 RECTANGULAR_PATTERN with pattern_count_v=4 and
pattern_spacing_v=0.0 collapses all V copies onto row 1. Receivers must
reject or warn-and-reclassify as 1-D pattern; silent acceptance is a
coverage gap.

Reproducer: 50×50 mm planar face host with a RECTANGULAR_PATTERN SHAPE_ASPECT
carrying pattern_count_u=3, pattern_count_v=4, pattern_spacing_u=10.0,
pattern_spacing_v=0.0.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi093",
    defect=(
        "RECTANGULAR_PATTERN SHAPE_ASPECT with pattern_count_v=4 and "
        "pattern_spacing_v=0.0 — zero V-spacing collapses 4 rows onto row 1; "
        "receiver must reject or warn-and-treat-as-1D-pattern"
    ),
)

# ── 50×50 mm planar face (host, area 2500 mm²) ───────────────────────────────
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

# ── DEFECT: RECTANGULAR_PATTERN with zero V-spacing ──────────────────────────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
pattern_asp = f._emit_raw("SHAPE_ASPECT('rectangular_pattern','',#9055,.T.)")

# Pattern count and spacing dimensions.
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'pattern_count_u')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('pattern_count_u',COUNT_MEASURE(3),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'pattern_spacing_u')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('pattern_spacing_u',LENGTH_MEASURE(10.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'pattern_count_v')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('pattern_count_v',COUNT_MEASURE(4),#9056)"
)
# DEFECT: zero spacing with count > 1
f._emit_raw(f"DIMENSIONAL_SIZE(#{pattern_asp.eid},'pattern_spacing_v')")
f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('pattern_spacing_v',LENGTH_MEASURE(0.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('pattern_on_face','pattern on host',"
    f"#{host_asp.eid},#{pattern_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('pattern_gisu',$,#{pattern_asp.eid},#9061,#{face.eid})"
)
