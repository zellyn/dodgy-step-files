"""Pmi104 — BOSS height = 0 (zero-protrusion boss).

Catalog claim: AP242 BOSS height must be strictly positive. This fixture emits
boss_height=0.0 mm and boss_diameter=12.0 mm. Receivers must reject and name
boss_height as the violated attribute; never substitute a default silently.

Byte assertions:
  contains(b'BOSS')
  contains(b'boss_height')
  contains(b'height_DEFECT_zero')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi104",
    defect=(
        "BOSS SHAPE_ASPECT with boss_height=0.0 mm (degenerate zero-protrusion); "
        "boss_height must be > 0; receiver must reject and name the violated attribute"
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

# ── DEFECT: BOSS with zero height ────────────────────────────────────────────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
boss_asp = f._emit_raw("SHAPE_ASPECT('BOSS','',#9055,.T.)")

f._emit_raw(f"DIMENSIONAL_SIZE(#{boss_asp.eid},'boss_diameter')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('boss_diameter',LENGTH_MEASURE(12.0),#9056)"
)
# boss_height = 0.0 mm — DEFECT (must be > 0)
f._emit_raw(f"DIMENSIONAL_SIZE(#{boss_asp.eid},'boss_height')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('height_DEFECT_zero',LENGTH_MEASURE(0.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('boss_on_face','boss on host',"
    f"#{host_asp.eid},#{boss_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('boss_gisu',$,#{boss_asp.eid},#9061,#{face.eid})"
)
