"""Pmi131 — THREAD claimed fit_class string outside standard set ('X1').

Catalog claim: AP242 thread fit_class must be from the standard set
(1A/2A/3A/1B/2B/3B for UN/UNJ, 4g6g/6g/5H6H/6H etc. for ISO metric).
This fixture emits fit_class='X1' — unrecognized. Receivers must reject
or drop with W_THREAD_UNKNOWN_FIT_CLASS; never silently propagate.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 899 and < 901

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi131",
    defect=(
        "thread SHAPE_ASPECT with fit_class='X1' — not in standard set "
        "(1A/2A/3A/1B/2B/3B or ISO metric grades); "
        "receiver must reject or drop with stable diagnostic"
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
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

host_asp   = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
thread_asp = f._emit_raw("SHAPE_ASPECT('thread','',#9055,.T.)")

# DEFECT: fit_class='X1' is not a recognized standard thread-fit designator
f._emit_raw(f"DIMENSIONAL_SIZE(#{thread_asp.eid},'nominal_diameter')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal_diameter',LENGTH_MEASURE(10.0),#9056)"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{thread_asp.eid},'pitch')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('pitch',LENGTH_MEASURE(1.5),#9056)"
)
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('fit_class','X1')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('thread_on_face','thread on host',"
    f"#{host_asp.eid},#{thread_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('thread_gisu',$,#{thread_asp.eid},#9061,#{face.eid})"
)
