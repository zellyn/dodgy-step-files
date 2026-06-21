"""Pmi100 — GROOVE feature with width = 0 (degenerate).

Catalog claim: AP242 GROOVE geometric invariant requires groove_width > 0.
This fixture emits groove_width=0.0 mm and groove_depth=2.0 mm. Receivers
must reject as degenerate and name groove_width; never substitute a default.

Byte assertions:
  contains(b'GROOVE')
  contains(b'groove_width')
  contains(b'width_DEFECT')

Tier-3 assertions:
  n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi100",
    defect=(
        "GROOVE SHAPE_ASPECT with groove_width=0.0 mm (degenerate zero-width groove); "
        "groove_width must be > 0; receiver must reject and name the violated attribute"
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

# ── DEFECT: GROOVE with zero width ───────────────────────────────────────────
host_asp  = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
groove_asp = f._emit_raw("SHAPE_ASPECT('GROOVE','',#9055,.T.)")

# width = 0.0 mm — the defect; marker string satisfies byte assertion
f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'groove_width')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('width_DEFECT',LENGTH_MEASURE(0.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{groove_asp.eid},'groove_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('groove_depth',LENGTH_MEASURE(2.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('groove_on_face','groove on host',"
    f"#{host_asp.eid},#{groove_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('groove_gisu',$,#{groove_asp.eid},#9061,#{face.eid})"
)
