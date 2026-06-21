"""Pmi105 — BOSS base not coplanar with host face (boss floats above substrate).

Catalog claim: AP242 BOSS AXIS2_PLACEMENT_3D base location must coincide with
the host face plane. This fixture places the boss base at (25.0, 25.0, 5.0)
while the host face is at z=0 — the boss is 5 mm above the face. Receivers
must reject or snap-and-warn; silent acceptance is forbidden.

Byte assertions:
  contains(b'BOSS')
  contains(b'boss_base_FLOATING')
  contains(b'AXIS2_PLACEMENT_3D')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi105",
    defect=(
        "BOSS AXIS2_PLACEMENT_3D base at (25,25,5) while host face is at z=0; "
        "boss base is 5 mm above the host face — floating boss; "
        "receiver must reject or snap-and-warn deterministically"
    ),
)

# ── 50×50 mm planar face host at z=0 ─────────────────────────────────────────
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

# ── DEFECT: BOSS base offset 5 mm above host face ────────────────────────────
# Boss center placed at z=5.0 (5 mm above the z=0 face) — floating boss.
boss_center = f.cartesian_point((25.0, 25.0, 5.0))  # z=5 not on face at z=0
boss_zdir   = f.direction((0.0, 0.0, 1.0))
boss_xdir   = f.direction((1.0, 0.0, 0.0))
boss_plc    = f.axis2_placement_3d(boss_center, boss_zdir, boss_xdir)

host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
boss_asp = f._emit_raw("SHAPE_ASPECT('BOSS','',#9055,.T.)")

# Embed the defect marker string for the byte assertion.
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM"
    "('boss_base_FLOATING','base_z=5.0 host_z=0.0 offset=5.0 mm')"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{boss_asp.eid},'boss_diameter')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('boss_diameter',LENGTH_MEASURE(12.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{boss_asp.eid},'boss_height')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('boss_height',LENGTH_MEASURE(8.0),#9056)"
)
# Link the defective placement to the boss feature.
# The AXIS2_PLACEMENT_3D with z=5.0 is the defective base.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('boss_placement','floating boss placement',"
    f"#{host_asp.eid},#{boss_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('boss_gisu',$,#{boss_asp.eid},#9061,#{face.eid})"
)
