"""Pmi103 — BOSS diameter smaller than host plate thickness (feature-class mismatch).

Catalog claim: AP242 BOSS conventional invariant: boss_diameter >= host_thickness.
This fixture emits boss_diameter=2.0 mm on a host with host_thickness=10.0 mm.
Receivers must warn W_BOSS_FEATURE_CLASS_MISMATCH and suggest reclassification
as stud/pin; never silently treat the feature as a heavy boss.

Byte assertions:
  contains(b'BOSS')
  contains(b'boss_diameter')
  contains(b'host_thickness')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi103",
    defect=(
        "BOSS SHAPE_ASPECT with boss_diameter=2.0 mm on a host with "
        "host_thickness=10.0 mm; diameter < host_thickness mis-classifies a stud "
        "as a boss; receiver must warn W_BOSS_FEATURE_CLASS_MISMATCH"
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

# ── DEFECT: BOSS with boss_diameter < host_thickness ─────────────────────────
host_asp = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
boss_asp = f._emit_raw("SHAPE_ASPECT('BOSS','',#9055,.T.)")

# boss_diameter = 2.0 mm — much smaller than host_thickness = 10 mm
f._emit_raw(f"DIMENSIONAL_SIZE(#{boss_asp.eid},'boss_diameter')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('boss_diameter',LENGTH_MEASURE(2.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{boss_asp.eid},'boss_height')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('boss_height',LENGTH_MEASURE(4.0),#9056)"
)
# host thickness context (the invariant is boss_diameter >= host_thickness)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('host_thickness','10.0 mm')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('boss_on_face','boss on host',"
    f"#{host_asp.eid},#{boss_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('boss_gisu',$,#{boss_asp.eid},#9061,#{face.eid})"
)
