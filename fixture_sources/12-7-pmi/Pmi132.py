"""Pmi132 — INTERNAL_THREAD declared on an EXTERNAL_THREAD-shaped host (gender mismatch).

Catalog claim: AP242 internal_thread must reference an internal (bore) host;
an external_thread must reference an external (boss) host. This fixture emits
SHAPE_ASPECT('internal_thread') whose GISU references a face tagged
host_kind='external_cylindrical_face' — gender contradiction. Receivers must
reject or emit W_THREAD_GENDER_MISMATCH; never silently machine a boss.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi132",
    defect=(
        "internal_thread SHAPE_ASPECT whose GISU references a face tagged "
        "host_kind='external_cylindrical_face'; gender contradiction — "
        "internal thread on external boss; receiver must reject"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((30.0, 0.0, 0.0))
p2 = f.cartesian_point((30.0, 30.0, 0.0)); p3 = f.cartesian_point((0.0, 30.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="external_boss_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

host_asp   = f._emit_raw("SHAPE_ASPECT('external_boss_face','',#9055,.T.)")
thread_asp = f._emit_raw("SHAPE_ASPECT('internal_thread','',#9055,.T.)")

# DEFECT: internal_thread gender F on host tagged as external (gender M) — contradiction
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('host_kind','external_cylindrical_face')"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{thread_asp.eid},'nominal_diameter')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal_diameter',LENGTH_MEASURE(10.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{thread_asp.eid},'pitch')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('pitch',LENGTH_MEASURE(1.5),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('thread_on_face','internal thread on host',"
    f"#{host_asp.eid},#{thread_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('thread_gisu',$,#{thread_asp.eid},#9061,#{face.eid})"
)
